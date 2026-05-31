import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { apiRequest, ApiError } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { employmentLabel, jobStatusLabel } from "../lib/labels";

type Job = Record<string, unknown>;

export default function JobDetailPage() {
  const { jobId } = useParams();
  const { userToken } = useAuth();
  const navigate = useNavigate();

  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  const [cover, setCover] = useState("");
  const [resumeUrl, setResumeUrl] = useState("");
  const [applyErr, setApplyErr] = useState<string | null>(null);
  const [applyOk, setApplyOk] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    let cancelled = false;
    if (!jobId) return;
    setLoading(true);
    apiRequest(`/public/jobs/${jobId}`, { method: "GET" })
      .then((data) => {
        if (!cancelled) setJob(data as Job);
      })
      .catch((e) => {
        if (!cancelled)
          setErr(e instanceof ApiError ? e.message : "Job not found");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [jobId]);

  async function submitApplication(e: FormEvent) {
    e.preventDefault();
    if (!userToken || !jobId) {
      navigate("/login");
      return;
    }
    setApplyErr(null);
    setApplyOk(false);
    setSubmitting(true);
    try {
      await apiRequest(`/applications/job/create`, {
        method: "POST",
        token: userToken,
        body: JSON.stringify({
          job_id: Number(jobId),
          status: 1,
          cover_letter: cover || null,
          resume_url: resumeUrl || null,
        }),
      });
      setApplyOk(true);
    } catch (e) {
      setApplyErr(e instanceof ApiError ? e.message : "Application failed");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <p style={{ color: "var(--text-muted)" }}>Loading listing…</p>;
  if (err || !job || !jobId)
    return (
      <>
        <p className="alert alert-error">{err ?? "Nothing here."}</p>
        <Link to="/">← Back</Link>
      </>
    );

  const title = String(job.title ?? "Role");
  const company = String(job.company_name ?? "Company");
  const location = String(job.location ?? "—");

  return (
    <>
      <div className="stack" style={{ marginBottom: "1rem" }}>
        <Link to="/" style={{ color: "var(--text-muted)" }}>
          ← All jobs
        </Link>
      </div>

      <article className="detail-shell">
        <div className="stack" style={{ marginBottom: "0.65rem", gap: "0.5rem" }}>
          <span className="pill">{employmentLabel(job.employment_type as never)}</span>
          <span className="pill">{jobStatusLabel(job.status as never)}</span>
        </div>
        <h1 className="display" style={{ fontSize: "2.2rem", marginBottom: "0.25rem" }}>
          {title}
        </h1>
        <p style={{ color: "var(--text-muted)", margin: 0 }}>
          {company} · {location}
        </p>

        {(job.application_url && String(job.application_url)) ||
        job.salary_range ||
        job.deadline ? (
          <div className="job-meta" style={{ marginTop: "1rem" }}>
            {job.salary_range && <span>{String(job.salary_range)}</span>}
            {job.deadline != null && job.deadline !== "" && (
              <span>Deadline {String(job.deadline)}</span>
            )}
            {job.application_url && (
              <a href={String(job.application_url)} target="_blank" rel="noreferrer">
                External posting
              </a>
            )}
          </div>
        ) : null}

        {"description" in job && (
          <div className="detail-desc">{String(job.description ?? "")}</div>
        )}
        {"requirements" in job && job.requirements ? (
          <div style={{ marginTop: "1.5rem" }}>
            <h2 style={{ fontSize: "1rem", marginBottom: "0.5rem" }}>Requirements</h2>
            <div className="detail-desc">{String(job.requirements)}</div>
          </div>
        ) : null}
      </article>

      <section className="detail-shell section-spacer-top" style={{ maxWidth: 760 }}>
        <h2 style={{ fontSize: "1.18rem", marginBottom: "0.75rem" }}>How to Apply</h2>
        {!userToken ? (
          <p style={{ color: "var(--text-muted)" }}>
            <Link to="/login">Sign in</Link>, complete profile and education onboarding, then
            return here to send your application.
          </p>
        ) : (
          <form className="form form-wide" onSubmit={submitApplication}>
            <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", margin: 0 }}>
              New applications post with <code>status: 1</code> (submitted).
            </p>
            <div className="field">
              <label>Cover letter (optional)</label>
              <textarea value={cover} onChange={(ev) => setCover(ev.target.value)} rows={5} />
            </div>
            <div className="field">
              <label>Résumé URL (optional)</label>
              <input
                type="url"
                value={resumeUrl}
                onChange={(ev) => setResumeUrl(ev.target.value)}
                placeholder="https://…"
              />
            </div>
            {applyErr && <div className="alert alert-error">{applyErr}</div>}
            {applyOk && (
              <div className="alert alert-success">
                Applied. Track status from your dashboard.
              </div>
            )}
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? "Submitting…" : "Submit application"}
            </button>
          </form>
        )}
      </section>
    </>
  );
}
