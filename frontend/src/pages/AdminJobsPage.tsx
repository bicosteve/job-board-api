import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { apiRequest, ApiError } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { applicationStatusLabel, employmentLabel } from "../lib/labels";

type JobRow = {
  job_id: number;
  title: string;
  company_name?: string;
  employment_type?: string | number;
};

type AppsInfo = {
  page: number;
  limit: number;
  count: number;
  applications: Record<string, unknown>[];
};

const EMPLOYMENT_TYPES = ["Full time", "Part time", "Contract", "Internship"] as const;
const JOB_STATUSES = ["Open", "Closed", "Draft"] as const;

export default function AdminJobsPage() {
  const { adminToken } = useAuth();

  const [jobs, setJobs] = useState<JobRow[]>([]);
  const [jobsLoading, setJobsLoading] = useState(true);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [requirements, setRequirements] = useState("");
  const [location, setLocation] = useState("");
  const [employmentType, setEmploymentType] =
    useState<(typeof EMPLOYMENT_TYPES)[number]>("Full time");
  const [salaryRange, setSalaryRange] = useState("");
  const [deadline, setDeadline] = useState(""); /* ISO yyyy-mm-dd from date input */
  const [companyName, setCompanyName] = useState("");
  const [jobStatus, setJobStatus] = useState<(typeof JOB_STATUSES)[number]>("Open");
  const [applicationUrl, setApplicationUrl] = useState("");

  const [createErr, setCreateErr] = useState<string | null>(null);
  const [createOk, setCreateOk] = useState<string | null>(null);

  const [selectedJobId, setSelectedJobId] = useState<number | "">("");
  const [appsPage, setAppsPage] = useState(1);
  const [appsInfo, setAppsInfo] = useState<AppsInfo | null>(null);
  const [appsErr, setAppsErr] = useState<string | null>(null);

  const [statusDraft, setStatusDraft] = useState<Record<number, number>>({});

  const loadJobs = useCallback(async () => {
    setJobsLoading(true);
    try {
      type R = { result: { jobs: JobRow[] } };
      const res = await apiRequest<R>(`/public/jobs?page=1&limit=100`, { method: "GET" });
      setJobs(Array.isArray(res.result?.jobs) ? res.result.jobs : []);
    } catch {
      setJobs([]);
    } finally {
      setJobsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadJobs();
  }, [loadJobs]);

  const numericSelectedId = typeof selectedJobId === "number" ? selectedJobId : 0;

  const loadApplications = useCallback(async () => {
    if (!numericSelectedId) {
      setAppsInfo(null);
      return;
    }
    setAppsErr(null);
    try {
      type R = { info: AppsInfo };
      const res = await apiRequest<R>(
        `/applications/job/list?job_id=${numericSelectedId}&page=${appsPage}&limit=10`,
        { method: "GET" }
      );
      setAppsInfo(res.info);
    } catch (e) {
      setAppsErr(e instanceof ApiError ? e.message : "Could not load applications");
      setAppsInfo(null);
    }
  }, [numericSelectedId, appsPage]);

  useEffect(() => {
    loadApplications();
  }, [loadApplications]);

  async function createJob(e: FormEvent) {
    e.preventDefault();
    if (!adminToken) return;
    setCreateErr(null);
    setCreateOk(null);
    try {
      const details: Record<string, unknown> = {
        description,
        requirements: requirements || null,
        location,
        employment_type: employmentType,
        salary_range: salaryRange || null,
        deadline: deadline ? deadline : null,
        status: jobStatus,
        company_name: companyName,
        application_url: applicationUrl || null,
      };
      await apiRequest(`/admin/jobs/create`, {
        method: "POST",
        token: adminToken,
        body: JSON.stringify({
          title,
          details,
        }),
      });
      setCreateOk("Published to MySQL ✓");
      setTitle("");
      setDescription("");
      setRequirements("");
      setLocation("");
      setSalaryRange("");
      setDeadline("");
      setCompanyName("");
      setApplicationUrl("");
      await loadJobs();
    } catch (err0) {
      setCreateErr(err0 instanceof ApiError ? err0.message : "Create failed");
    }
  }

  async function patchApplication(applicationId: number, currentStatus: number) {
    if (!adminToken) return;
    const status = statusDraft[applicationId] ?? currentStatus;
    if (status === currentStatus) return;
    setAppsErr(null);
    try {
      await apiRequest(`/applications/job/update/${applicationId}`, {
        method: "PUT",
        token: adminToken,
        body: JSON.stringify({ status }),
      });
      await loadApplications();
    } catch (e) {
      setAppsErr(e instanceof ApiError ? e.message : "Update failed");
    }
  }

  const jobOptions = useMemo(
    () =>
      [...jobs].sort((a, b) => Number(a.job_id) - Number(b.job_id)),
    [jobs]
  );

  return (
    <>
      <div className="headline-row">
        <div>
          <h1 className="display">Admin postings</h1>
          <p className="tagline">
            Publish roles and move candidates through each hiring stage with a clear workflow.
          </p>
        </div>
        <div className="stack">
          <Link to="/" className="btn btn-secondary">
            ← Public jobs
          </Link>
        </div>
      </div>

      <section className="detail-shell section-spacer-bottom">
        <h2 style={{ fontSize: "1.05rem", marginBottom: "1rem" }}>Publish listing</h2>
        <form className="form form-wide" onSubmit={createJob}>
          <div className="field">
            <label>Title</label>
            <input value={title} onChange={(ev) => setTitle(ev.target.value)} required />
          </div>
          <div className="field">
            <label>Company</label>
            <input value={companyName} onChange={(ev) => setCompanyName(ev.target.value)} required />
          </div>
          <div className="field-inline">
            <div className="field">
              <label>Location</label>
              <input value={location} onChange={(ev) => setLocation(ev.target.value)} required />
            </div>
            <div className="field">
              <label>Employment</label>
              <select
                value={employmentType}
                onChange={(ev) =>
                  setEmploymentType(ev.target.value as (typeof EMPLOYMENT_TYPES)[number])
                }
              >
                {EMPLOYMENT_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="field">
            <label>Description</label>
            <textarea value={description} onChange={(ev) => setDescription(ev.target.value)} required rows={6} />
          </div>
          <div className="field">
            <label>Requirements (optional)</label>
            <textarea value={requirements} onChange={(ev) => setRequirements(ev.target.value)} rows={3} />
          </div>
          <div className="field-inline">
            <div className="field">
              <label>Salary range (optional, min length 3 if set)</label>
              <input
                value={salaryRange}
                onChange={(ev) => setSalaryRange(ev.target.value)}
                placeholder="e.g. $120k–$150k USD"
              />
            </div>
            <div className="field">
              <label>Deadline (optional)</label>
              <input type="date" value={deadline} onChange={(ev) => setDeadline(ev.target.value)} />
            </div>
          </div>
          <div className="field-inline">
            <div className="field">
              <label>Pipeline status</label>
              <select
                value={jobStatus}
                onChange={(ev) => setJobStatus(ev.target.value as (typeof JOB_STATUSES)[number])}
              >
                {JOB_STATUSES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>External posting URL</label>
              <input type="url" value={applicationUrl} onChange={(ev) => setApplicationUrl(ev.target.value)} />
            </div>
          </div>
          {createErr && <div className="alert alert-error">{createErr}</div>}
          {createOk && <div className="alert alert-success">{createOk}</div>}
          <button type="submit" className="btn btn-primary">
            Submit to API
          </button>
        </form>
      </section>

      <section className="detail-shell">
        <h2 style={{ fontSize: "1.05rem", marginBottom: "0.85rem" }}>Applications pipeline</h2>
        <div className="field" style={{ maxWidth: 420 }}>
          <label>Pick job ({jobsLoading ? "loading…" : `${jobOptions.length} rows`})</label>
          <select
            value={selectedJobId === "" ? "" : String(selectedJobId)}
            onChange={(ev) => {
              const v = ev.target.value;
              setSelectedJobId(v ? Number(v) : "");
              setAppsPage(1);
            }}
          >
            <option value="">Select job…</option>
            {jobOptions.map((j) => (
              <option key={j.job_id} value={j.job_id}>
                #{j.job_id} · {j.title}{" "}
                {j.company_name ? `· ${j.company_name}` : ""}{" "}
                {employmentLabel(j.employment_type as never)}
              </option>
            ))}
          </select>
        </div>

        {appsErr && <div className="alert alert-error" style={{ marginTop: "0.85rem" }}>{appsErr}</div>}

        {appsInfo && (
          <>
            <p style={{ fontSize: "0.875rem", color: "var(--text-muted)", marginTop: "0.85rem" }}>
              Job #{numericSelectedId} · page {appsInfo.page}, {appsInfo.count} row(s) on this page.
            </p>

            <div className="table-wrap" style={{ marginTop: "0.85rem" }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Application</th>
                    <th>User</th>
                    <th>Current</th>
                    <th>Move to…</th>
                  </tr>
                </thead>
                <tbody>
                  {appsInfo.applications.map((app) => {
                    const aid = Number(app.application_id);
                    const uid = String(app.user_id ?? "—");
                    const current = Number(app.status ?? 1);
                    const selected = statusDraft[aid] ?? current;
                    return (
                      <tr key={aid}>
                        <td>{aid}</td>
                        <td>{uid}</td>
                        <td>{applicationStatusLabel(current)}</td>
                        <td>
                          <div className="stack">
                            <select
                              style={{
                                padding: "0.35rem 0.55rem",
                                borderRadius: 8,
                                border: "1px solid var(--border)",
                                background: "var(--bg-elevated)",
                                color: "var(--text)",
                              }}
                              value={[1, 2, 3, 4].includes(selected) ? selected : 1}
                              onChange={(ev) =>
                                setStatusDraft((d) => ({
                                  ...d,
                                  [aid]: Number(ev.target.value),
                                }))
                              }
                            >
                              {[1, 2, 3, 4].map((s) => (
                                <option key={s} value={s}>
                                  {applicationStatusLabel(s)}
                                </option>
                              ))}
                            </select>
                            <button
                              type="button"
                              className="btn btn-secondary"
                              disabled={
                                adminToken == null || selected === current
                              }
                              onClick={() => patchApplication(aid, current)}
                            >
                              Save
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <div className="stack" style={{ marginTop: "1rem" }}>
              <button
                type="button"
                className="btn btn-secondary"
                disabled={appsPage <= 1}
                onClick={() => setAppsPage((p) => Math.max(1, p - 1))}
              >
                Prev
              </button>
              <span style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>Page {appsPage}</span>
              <button
                type="button"
                className="btn btn-secondary"
                disabled={appsInfo.count < appsInfo.limit}
                onClick={() => setAppsPage((p) => p + 1)}
              >
                Next
              </button>
              <button type="button" className="btn btn-ghost" onClick={() => loadApplications()}>
                Refresh
              </button>
            </div>
          </>
        )}
      </section>
    </>
  );
}
