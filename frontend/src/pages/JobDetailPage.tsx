import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { apiRequest, apiUploadFile, ApiError } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { employmentLabel, jobStatusLabel } from "../lib/labels";

type Job = Record<string, unknown>;

function statusPillClass(code: string | number | undefined | null): string {
  const label = jobStatusLabel(code).toLowerCase();
  if (label === "open")   return "pill status-open";
  if (label === "closed") return "pill status-closed";
  if (label === "draft")  return "pill status-draft";
  return "pill";
}

export default function JobDetailPage() {
  const { jobId } = useParams();
  const { userToken } = useAuth();
  const navigate = useNavigate();

  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  const [cover, setCover] = useState("");
  const [resumeUrl, setResumeUrl] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [applyErr, setApplyErr] = useState<string | null>(null);
  const [applyOk, setApplyOk] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    if (!jobId) return;
    setLoading(true);
    apiRequest(`/public/jobs/${jobId}`, { method: "GET" })
      .then((data) => { if (!cancelled) setJob(data as Job); })
      .catch((e) => { if (!cancelled) setErr(e instanceof ApiError ? e.message : "Job not found"); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [jobId]);

  async function submitApplication(e: FormEvent) {
    e.preventDefault();
    if (!userToken || !jobId) { navigate("/login"); return; }
    setApplyErr(null);
    setApplyOk(false);
    setSubmitting(true);

    try {
      let finalResumeUrl = resumeUrl;
      if (resumeFile) {
        setUploading(true);
        const upload = await apiUploadFile<{ file_url: string }>(`/files/upload`, resumeFile, {
          token: userToken,
        });
        finalResumeUrl = upload.file_url;
        setUploading(false);
      }

      await apiRequest(`/applications/job/create`, {
        method: "POST",
        token: userToken,
        body: JSON.stringify({
          job_id: Number(jobId),
          status: 1,
          cover_letter: cover || null,
          resume_url: finalResumeUrl || null,
        }),
      });
      setApplyOk(true);
      setResumeFile(null);
    } catch (e) {
      setApplyErr(e instanceof ApiError ? e.message : "Application failed");
      setUploading(false);
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <div>
        <div className="stack" style={{ marginBottom: "1.25rem" }}>
          <Link to="/" style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>← All jobs</Link>
        </div>
        <div className="job-detail-hero">
          <div className="skeleton-logo" style={{ width: 64, height: 64 }} />
          <div className="skeleton-line" style={{ width: "55%", height: 20, marginTop: 16 }} />
          <div className="skeleton-line" style={{ width: "35%", height: 14, marginTop: 10 }} />
        </div>
      </div>
    );
  }

  if (err || !job || !jobId) {
    return (
      <>
        <div className="alert alert-error">{err ?? "Nothing here."}</div>
        <Link to="/" className="btn btn-secondary" style={{ marginTop: "1rem" }}>← Back to jobs</Link>
      </>
    );
  }

  const title   = String(job.title ?? "Role");
  const company = String(job.company_name ?? "Company");
  const loc     = String(job.location ?? "—");

  return (
    <>
      {/* Breadcrumb */}
      <div className="stack" style={{ marginBottom: "1.25rem" }}>
        <Link to="/" style={{ color: "var(--text-muted)", fontSize: "0.88rem" }}>
          ← Back to jobs
        </Link>
      </div>

      {/* ── HERO HEADER ── */}
      <div className="job-detail-hero">
        <div style={{ display: "flex", gap: "1.25rem", alignItems: "flex-start", flexWrap: "wrap" }}>
          <div className="job-detail-logo" aria-hidden>
            {company.trim().charAt(0).toUpperCase()}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className="stack" style={{ marginBottom: "0.6rem" }}>
              <span className={statusPillClass(job.status as never)}>
                {jobStatusLabel(job.status as never)}
              </span>
              <span className="pill pill-accent">
                {employmentLabel(job.employment_type as never)}
              </span>
            </div>
            <h1 className="job-detail-title">{title}</h1>
            <div className="job-detail-meta-row">
              <span style={{ fontWeight: 500 }}>{company}</span>
              <span className="job-detail-meta-sep" aria-hidden />
              <span>{loc}</span>
              {job.salary_range != null && (
                <>
                  <span className="job-detail-meta-sep" aria-hidden />
                  <span style={{ color: "var(--success)", fontWeight: 500 }}>
                    {String(job.salary_range)}
                  </span>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ── TWO-COLUMN LAYOUT ── */}
      <div className="job-detail-layout">
        {/* Main content */}
        <div className="job-detail-main">
          {/* Description */}
          <div className="detail-shell section-spacer-bottom">
            <div className="section-head">
              <h2>About this role</h2>
            </div>
            {"description" in job && (
              <div className="detail-desc">{String(job.description ?? "")}</div>
            )}
          </div>

          {/* Requirements */}
          {"requirements" in job && job.requirements != null && (
            <div className="detail-shell section-spacer-bottom">
              <div className="section-head">
                <h2>Requirements</h2>
              </div>
              <div className="detail-desc">{String(job.requirements)}</div>
            </div>
          )}

          {/* Apply form */}
          <div className="detail-shell">
            <div className="section-head">
              <div>
                <h2>Apply for this role</h2>
                <p className="section-head-sub">
                  {userToken
                    ? "Submit your application below"
                    : "Sign in to your account to apply"}
                </p>
              </div>
            </div>

            {!userToken ? (
              <div style={{ padding: "1rem 0" }}>
                <p style={{ color: "var(--text-muted)", marginBottom: "1.25rem", fontSize: "0.95rem" }}>
                  You need a verified account to apply. Complete profile and education onboarding
                  first, then return here.
                </p>
                <div className="stack">
                  <Link to="/login" className="btn btn-primary">Sign in to apply</Link>
                  <Link to="/register" className="btn btn-secondary">Create account</Link>
                </div>
              </div>
            ) : applyOk ? (
              <div className="alert alert-success" style={{ fontSize: "1rem", padding: "1.1rem 1.25rem" }}>
                <span>✓</span>
                <div>
                  <strong>Application submitted!</strong>
                  <p style={{ margin: "0.25rem 0 0", fontSize: "0.88rem" }}>
                    Track the status from your{" "}
                    <Link to="/dashboard">dashboard</Link>.
                  </p>
                </div>
              </div>
            ) : (
              <form className="form" style={{ maxWidth: 640 }} onSubmit={submitApplication}>
                <div className="field">
                  <label>Cover letter <span style={{ color: "var(--text-faint)", fontSize: "0.75rem" }}>(optional)</span></label>
                  <textarea
                    value={cover}
                    onChange={(ev) => setCover(ev.target.value)}
                    rows={5}
                    placeholder="Tell the employer why you're a great fit…"
                  />
                </div>
                <div className="field">
                  <label>Résumé URL <span style={{ color: "var(--text-faint)", fontSize: "0.75rem" }}>(optional)</span></label>
                  <input
                    type="url"
                    value={resumeUrl}
                    onChange={(ev) => setResumeUrl(ev.target.value)}
                    placeholder="https://your-resume.pdf"
                  />
                </div>
                <div className="field">
                  <label>Upload résumé <span style={{ color: "var(--text-faint)", fontSize: "0.75rem" }}>(optional)</span></label>
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx,.txt"
                    onChange={(ev) => setResumeFile(ev.target.files?.[0] ?? null)}
                  />
                  {resumeFile && (
                    <div style={{ marginTop: "0.55rem", color: "var(--text-muted)", fontSize: "0.85rem" }}>
                      Selected file: {resumeFile.name}
                    </div>
                  )}
                </div>
                {applyErr && <div className="alert alert-error">{applyErr}</div>}
                <div className="stack">
                  <button type="submit" className="btn btn-primary" disabled={submitting || uploading}>
                    {submitting ? "Submitting…" : "Submit application →"}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <aside className="job-detail-sidebar">
          {/* Job info card */}
          <div className="job-info-card">
            <p className="section-label" style={{ marginBottom: "0.75rem" }}>Role details</p>

            <div className="job-info-row">
              <span className="job-info-label">Company</span>
              <span className="job-info-value">{company}</span>
            </div>
            <div className="job-info-row">
              <span className="job-info-label">Location</span>
              <span className="job-info-value">{loc}</span>
            </div>
            <div className="job-info-row">
              <span className="job-info-label">Type</span>
              <span className="job-info-value">{employmentLabel(job.employment_type as never)}</span>
            </div>
            {job.salary_range != null && (
              <div className="job-info-row">
                <span className="job-info-label">Salary</span>
                <span className="job-info-value" style={{ color: "var(--success)" }}>
                  {String(job.salary_range)}
                </span>
              </div>
            )}
            {job.deadline != null && job.deadline !== "" && (
              <div className="job-info-row">
                <span className="job-info-label">Deadline</span>
                <span className="job-info-value">{String(job.deadline)}</span>
              </div>
            )}
            <div className="job-info-row">
              <span className="job-info-label">Status</span>
              <span className="job-info-value">
                <span className={statusPillClass(job.status as never)}>{jobStatusLabel(job.status as never)}</span>
              </span>
            </div>
          </div>

          {/* External link */}
          {job.application_url != null && (
            <a
              href={String(job.application_url)}
              target="_blank"
              rel="noreferrer"
              className="btn btn-secondary"
              style={{ width: "100%", justifyContent: "center" }}
            >
              External posting ↗
            </a>
          )}

          {/* CTA for signed-out users */}
          {!userToken && (
            <div className="job-info-card" style={{ textAlign: "center" }}>
              <p style={{ margin: "0 0 1rem", fontSize: "0.9rem", color: "var(--text-muted)" }}>
                Ready to apply? Create your free account.
              </p>
              <Link to="/register" className="btn btn-primary" style={{ width: "100%", justifyContent: "center" }}>
                Get started →
              </Link>
            </div>
          )}
        </aside>
      </div>
    </>
  );
}
