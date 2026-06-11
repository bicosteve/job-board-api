import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { apiRequest, ApiError, getApiBase } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { applicationStatusLabel, employmentLabel } from "../lib/labels";

type JobRow = {
  job_id: number;
  title: string;
  company_name?: string;
  employment_type?: string | number;
};

type ApplicationRow = {
  application_id: number;
  user_id: number;
  job_id?: number;
  status: number;
  cover_letter?: string;
  applicant_email?: string;
  applicant_first_name?: string;
  applicant_last_name?: string;
  applicant_cv_url?: string;
  resume_url?: string;
};

type AppsInfo = {
  page: number;
  limit: number;
  count: number;
  applications: ApplicationRow[];
};

const EMPLOYMENT_TYPES = ["Full time", "Part time", "Contract", "Internship"] as const;
const JOB_STATUSES     = ["Open", "Closed", "Draft"] as const;

function appStatusClass(status: number | string | undefined): string {
  const n = Number(status);
  if (n === 1) return "pill status-submitted";
  if (n === 2) return "pill status-review";
  if (n === 3) return "pill status-interview";
  if (n === 4) return "pill status-decision";
  return "pill pill-subtle";
}

export default function AdminJobsPage() {
  const { adminToken } = useAuth();

  const [jobs, setJobs]               = useState<JobRow[]>([]);
  const [jobsLoading, setJobsLoading] = useState(true);
  const [liveConnected, setLiveConnected] = useState(false);

  const [title, setTitle]                     = useState("");
  const [description, setDescription]         = useState("");
  const [requirements, setRequirements]       = useState("");
  const [location, setLocation]               = useState("");
  const [employmentType, setEmploymentType]   = useState<(typeof EMPLOYMENT_TYPES)[number]>("Full time");
  const [salaryRange, setSalaryRange]         = useState("");
  const [deadline, setDeadline]               = useState("");
  const [companyName, setCompanyName]         = useState("");
  const [jobStatus, setJobStatus]             = useState<(typeof JOB_STATUSES)[number]>("Open");
  const [applicationUrl, setApplicationUrl]   = useState("");

  const [createErr, setCreateErr]             = useState<string | null>(null);
  const [createOk, setCreateOk]               = useState<string | null>(null);
  const [createSubmitting, setCreateSubmitting] = useState(false);

  const [selectedJobId, setSelectedJobId]     = useState<number | "">("");
  const [appsPage, setAppsPage]               = useState(1);
  const [appsInfo, setAppsInfo]               = useState<AppsInfo | null>(null);
  const [appsErr, setAppsErr]                 = useState<string | null>(null);
  const [statusDraft, setStatusDraft]         = useState<Record<number, number>>({});  const [selectedApplication, setSelectedApplication] = useState<ApplicationRow | null>(null);
  const loadJobs = useCallback(async () => {
    setJobsLoading(true);
    try {
      type R = { result: { jobs: JobRow[] } };
      const res = await apiRequest<R>(`/admin/jobs/list?page=1&limit=100`, {
        method: "GET",
        token: adminToken,
      });
      setJobs(Array.isArray(res.result?.jobs) ? res.result.jobs : []);
    } catch {
      setJobs([]);
    } finally {
      setJobsLoading(false);
    }
  }, [adminToken]);

  useEffect(() => { loadJobs(); }, [loadJobs]);

  const numericSelectedId = typeof selectedJobId === "number" ? selectedJobId : 0;

  const loadApplications = useCallback(async () => {
    if (!numericSelectedId) { setAppsInfo(null); return; }
    setAppsErr(null);
    try {
      type R = { info: AppsInfo };
      const res = await apiRequest<R>(
        `/applications/job/list?job_id=${numericSelectedId}&page=${appsPage}&limit=10`,
        { method: "GET", token: adminToken }
      );
      setAppsInfo(res.info);
    } catch (e) {
      setAppsErr(e instanceof ApiError ? e.message : "Could not load applications");
      setAppsInfo(null);
    }
  }, [numericSelectedId, appsPage, adminToken]);

  useEffect(() => { loadApplications(); }, [loadApplications]);

  useEffect(() => {
    if (!adminToken || !numericSelectedId) { setLiveConnected(false); return; }
    const source = new EventSource(
      `${getApiBase()}/applications/admin/stream?token=${encodeURIComponent(adminToken)}&job_id=${numericSelectedId}`
    );
    source.onopen    = () => setLiveConnected(true);
    source.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data) as AppsInfo;
        if (payload?.applications) setAppsInfo(payload);
      } catch { /* ignore */ }
    };
    source.onerror = () => { setLiveConnected(false); source.close(); };
    return () => { source.close(); setLiveConnected(false); };
  }, [adminToken, numericSelectedId]);

  async function createJob(e: FormEvent) {
    e.preventDefault();
    if (!adminToken) return;
    setCreateErr(null);
    setCreateOk(null);
    setCreateSubmitting(true);
    try {
      await apiRequest(`/admin/jobs/create`, {
        method: "POST",
        token: adminToken,
        body: JSON.stringify({
          title,
          details: {
            description,
            requirements: requirements || null,
            location,
            employment_type: employmentType,
            salary_range: salaryRange || null,
            deadline: deadline || null,
            status: jobStatus,
            company_name: companyName,
            application_url: applicationUrl || null,
          },
        }),
      });
      setCreateOk("Job published successfully ✓");
      setTitle(""); setDescription(""); setRequirements(""); setLocation("");
      setSalaryRange(""); setDeadline(""); setCompanyName(""); setApplicationUrl("");
      await loadJobs();
    } catch (err0) {
      setCreateErr(err0 instanceof ApiError ? err0.message : "Create failed");
    } finally {
      setCreateSubmitting(false);
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
    () => [...jobs].sort((a, b) => Number(a.job_id) - Number(b.job_id)),
    [jobs]
  );

  return (
    <div className="dashboard-grid">
      {/* ── HEADER ── */}
      <div className="headline-row">
        <div>
          <p className="section-label">Employer console</p>
          <h1 className="display">Admin postings</h1>
          <p className="tagline">
            Publish roles and move candidates through each hiring stage.
          </p>
        </div>
        <div className="stack" style={{ alignSelf: "flex-end" }}>
          <span className={`live-indicator ${liveConnected ? "connected" : "reconnecting"}`}>
            <span className="live-dot" />
            {liveConnected ? "Feed live" : "Reconnecting"}
          </span>
          <Link to="/" className="btn btn-secondary">← Public jobs</Link>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-strip">
        <div className="stat-card">
          <div className="stat-card-icon stat-card-icon-blue">📌</div>
          <div className="stat-card-value">{jobsLoading ? "—" : jobs.length}</div>
          <div className="stat-card-label">Total listings</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-icon stat-card-icon-green">
            {numericSelectedId ? "🔴" : "○"}
          </div>
          <div className="stat-card-value">
            {numericSelectedId ? String(appsInfo?.count ?? "—") : "—"}
          </div>
          <div className="stat-card-label">Applications (selected job)</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-icon stat-card-icon-purple"></div>
          <div className="stat-card-value">{liveConnected ? "On" : "Off"}</div>
          <div className="stat-card-label">Live stream</div>
        </div>
      </div>

      {/* ── PUBLISH JOB ── */}
      <section className="detail-shell">
        <div className="section-head">
          <div>
            <h2>Publish a listing</h2>
            <p className="section-head-sub">Fill in the details and submit to the live board</p>
          </div>
        </div>

        <form className="form form-wide" onSubmit={createJob}>
          {/* Row 1 */}
          <div className="field-inline">
            <div className="field">
              <label>Job title</label>
              <input
                value={title}
                onChange={(ev) => setTitle(ev.target.value)}
                placeholder="e.g. Senior Product Designer"
                required
              />
            </div>
            <div className="field">
              <label>Company name</label>
              <input
                value={companyName}
                onChange={(ev) => setCompanyName(ev.target.value)}
                placeholder="e.g. Acme Corp"
                required
              />
            </div>
          </div>

          {/* Row 2 */}
          <div className="field-inline">
            <div className="field">
              <label>Location</label>
              <input
                value={location}
                onChange={(ev) => setLocation(ev.target.value)}
                placeholder="e.g. New York, NY or Remote"
                required
              />
            </div>
            <div className="field">
              <label>Employment type</label>
              <select
                value={employmentType}
                onChange={(ev) => setEmploymentType(ev.target.value as (typeof EMPLOYMENT_TYPES)[number])}
              >
                {EMPLOYMENT_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
          </div>

          {/* Description */}
          <div className="field">
            <label>Job description</label>
            <textarea
              value={description}
              onChange={(ev) => setDescription(ev.target.value)}
              required
              rows={6}
              placeholder="Describe the role, responsibilities, and what success looks like…"
            />
          </div>

          {/* Requirements */}
          <div className="field">
            <label>
              Requirements <span style={{ color: "var(--text-faint)", fontSize: "0.75rem" }}>(optional)</span>
            </label>
            <textarea
              value={requirements}
              onChange={(ev) => setRequirements(ev.target.value)}
              rows={3}
              placeholder="List key qualifications, tools, or experience required…"
            />
          </div>

          {/* Row 3 */}
          <div className="field-inline">
            <div className="field">
              <label>
                Salary range <span style={{ color: "var(--text-faint)", fontSize: "0.75rem" }}>(optional)</span>
              </label>
              <input
                value={salaryRange}
                onChange={(ev) => setSalaryRange(ev.target.value)}
                placeholder="e.g. $120k–$150k USD"
              />
            </div>
            <div className="field">
              <label>
                Application deadline <span style={{ color: "var(--text-faint)", fontSize: "0.75rem" }}>(optional)</span>
              </label>
              <input type="date" value={deadline} onChange={(ev) => setDeadline(ev.target.value)} />
            </div>
          </div>

          {/* Row 4 */}
          <div className="field-inline">
            <div className="field">
              <label>Pipeline status</label>
              <select
                value={jobStatus}
                onChange={(ev) => setJobStatus(ev.target.value as (typeof JOB_STATUSES)[number])}
              >
                {JOB_STATUSES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="field">
              <label>
                External posting URL <span style={{ color: "var(--text-faint)", fontSize: "0.75rem" }}>(optional)</span>
              </label>
              <input
                type="url"
                value={applicationUrl}
                onChange={(ev) => setApplicationUrl(ev.target.value)}
                placeholder="https://…"
              />
            </div>
          </div>

          {createErr && <div className="alert alert-error">{createErr}</div>}
          {createOk  && <div className="alert alert-success">✓ {createOk}</div>}

          <div className="stack">
            <button type="submit" className="btn btn-primary" disabled={createSubmitting}>
              {createSubmitting ? "Publishing…" : "Publish listing →"}
            </button>
          </div>
        </form>
      </section>

      {/* ── APPLICATIONS PIPELINE ── */}
      <section className="detail-shell">
        <div className="section-head">
          <div>
            <h2>Applications pipeline</h2>
            <p className="section-head-sub">Select a job to view and manage candidates</p>
          </div>
          {numericSelectedId > 0 && (
            <button type="button" className="btn btn-ghost" onClick={() => loadApplications()}>
              ↻ Refresh
            </button>
          )}
        </div>

        {/* Job selector */}
        <div className="pipeline-select-wrap">
          <div className="field">
            <label>
              Select job to manage{" "}
              <span style={{ color: "var(--text-faint)", fontSize: "0.75rem" }}>
                ({jobsLoading ? "loading…" : `${jobOptions.length} listings`})
              </span>
            </label>
            <select
              value={selectedJobId === "" ? "" : String(selectedJobId)}
              onChange={(ev) => {
                const v = ev.target.value;
                setSelectedJobId(v ? Number(v) : "");
                setAppsPage(1);
              }}
            >
              <option value="">Choose a job listing…</option>
              {jobOptions.map((j) => (
                <option key={j.job_id} value={j.job_id}>
                  #{j.job_id} · {j.title}
                  {j.company_name ? ` (${j.company_name})` : ""}{" "}
                  — {employmentLabel(j.employment_type as never)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {appsErr && (
          <div className="alert alert-error" style={{ marginBottom: "1rem" }}>{appsErr}</div>
        )}

        {!numericSelectedId && (
          <div style={{ padding: "2rem 1rem", textAlign: "center", color: "var(--text-muted)" }}>
            <p style={{ margin: 0, fontSize: "0.95rem" }}>
              Select a listing above to view its candidate pipeline.
            </p>
          </div>
        )}

        {appsInfo && (
          <>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.85rem", flexWrap: "wrap" }}>
              <span style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
                Job #{numericSelectedId} · <strong style={{ color: "var(--text)" }}>{appsInfo.count}</strong> application{appsInfo.count === 1 ? "" : "s"} on page {appsInfo.page}
              </span>
              <span className={`live-indicator ${liveConnected ? "connected" : "reconnecting"}`} style={{ fontSize: "0.72rem" }}>
                <span className="live-dot" />
                {liveConnected ? "Live" : "Offline"}
              </span>
            </div>

            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>App #</th>
                    <th>Candidate</th>
                    <th>Contact</th>
                    <th>Resume</th>
                    <th>Details</th>
                    <th>Current stage</th>
                    <th>Move to…</th>
                  </tr>
                </thead>
                <tbody>
                  {appsInfo.applications.map((app) => {
                    const aid      = Number(app.application_id);
                    const current  = Number(app.status ?? 1);
                    const selected = statusDraft[aid] ?? current;
                    const candidateName = app.applicant_first_name || app.applicant_last_name
                      ? `${String(app.applicant_first_name ?? "")} ${String(app.applicant_last_name ?? "")}`.trim()
                      : `User #${String(app.user_id ?? "—")}`;
                    const candidateEmail = String(app.applicant_email ?? "—");
                    const resumeLink = String(app.resume_url ?? app.applicant_cv_url ?? "");
                    return (
                      <tr key={aid}>
                        <td style={{ fontFamily: "monospace", fontSize: "0.82rem", color: "var(--text-faint)" }}>
                          #{aid}
                        </td>
                        <td style={{ fontWeight: 500 }}>{candidateName}</td>
                        <td style={{ fontSize: "0.92rem", color: "var(--text-faint)" }}>{candidateEmail}</td>
                        <td>
                          {resumeLink ? (
                            <a href={resumeLink} target="_blank" rel="noreferrer" className="link-secondary">
                              View CV ↗
                            </a>
                          ) : (
                            <span style={{ color: "var(--text-muted)" }}>No resume</span>
                          )}
                        </td>
                        <td>
                          <button
                            type="button"
                            className="btn btn-ghost"
                            onClick={() => setSelectedApplication(app)}
                          >
                            View details
                          </button>
                        </td>
                        <td>
                          <span className={appStatusClass(current)}>
                            {applicationStatusLabel(current)}
                          </span>
                        </td>
                        <td>
                          <div className="stack">
                            <select
                              style={{
                                padding: "0.38rem 0.65rem",
                                borderRadius: "var(--radius-sm)",
                                border: "1px solid var(--border)",
                                background: "var(--bg-elevated)",
                                color: "var(--text)",
                                fontSize: "0.85rem",
                              }}
                              value={[1,2,3,4].includes(selected) ? selected : 1}
                              onChange={(ev) =>
                                setStatusDraft((d) => ({ ...d, [aid]: Number(ev.target.value) }))
                              }
                            >
                              {[1,2,3,4].map((s) => (
                                <option key={s} value={s}>{applicationStatusLabel(s)}</option>
                              ))}
                            </select>
                            <button
                              type="button"
                              className="btn btn-primary"
                              style={{ padding: "0.38rem 0.9rem", fontSize: "0.82rem" }}
                              disabled={adminToken == null || selected === current}
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
                ← Prev
              </button>
              <span style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
                Page {appsPage}
              </span>
              <button
                type="button"
                className="btn btn-secondary"
                disabled={appsInfo.count < appsInfo.limit}
                onClick={() => setAppsPage((p) => p + 1)}
              >
                Next →
              </button>
            </div>
          </>
        )}

        {selectedApplication && (
          <div className="modal-backdrop" role="dialog" aria-modal="true">
            <div className="modal">
              <div className="modal-header">
                <div>
                  <p className="section-label">Applicant details</p>
                  <h3>{selectedApplication.applicant_first_name || selectedApplication.applicant_last_name ?
                    `${selectedApplication.applicant_first_name ?? ""} ${selectedApplication.applicant_last_name ?? ""}`.trim() :
                    `Applicant #${selectedApplication.user_id}`}
                  </h3>
                  <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "0.95rem" }}>
                    Application ID #{selectedApplication.application_id}
                  </p>
                </div>
                <button
                  type="button"
                  className="btn btn-ghost"
                  onClick={() => setSelectedApplication(null)}
                >
                  Close
                </button>
              </div>

              <div className="modal-content">
                <div className="modal-row">
                  <span>Candidate email</span>
                  <strong>{selectedApplication.applicant_email ?? "—"}</strong>
                </div>
                <div className="modal-row">
                  <span>Resume link</span>
                  {selectedApplication.resume_url ? (
                    <a href={selectedApplication.resume_url} target="_blank" rel="noreferrer">
                      Open application resume ↗
                    </a>
                  ) : (
                    <span>No application resume provided</span>
                  )}
                </div>
                <div className="modal-row">
                  <span>Profile CV</span>
                  {selectedApplication.applicant_cv_url ? (
                    <a href={selectedApplication.applicant_cv_url} target="_blank" rel="noreferrer">
                      Open profile CV ↗
                    </a>
                  ) : (
                    <span>No profile CV uploaded</span>
                  )}
                </div>
                <div className="modal-row">
                  <span>Cover letter</span>
                  <div className="modal-copy">
                    {selectedApplication.cover_letter ? selectedApplication.cover_letter : "No cover letter provided."}
                  </div>
                </div>
                <div className="modal-row">
                  <span>Status</span>
                  <span className={appStatusClass(selectedApplication.status)}>
                    {applicationStatusLabel(selectedApplication.status)}
                  </span>
                </div>
              </div>

              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setSelectedApplication(null)}>
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
