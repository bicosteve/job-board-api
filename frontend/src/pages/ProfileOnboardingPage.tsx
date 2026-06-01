import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { apiRequest, apiUploadFile, ApiError } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function ProfileOnboardingPage() {
  const { userToken } = useAuth();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName]   = useState("");
  const [cvUrl, setCvUrl]         = useState("");
  const [cvFile, setCvFile]       = useState<File | null>(null);
  const [err, setErr]             = useState<string | null>(null);
  const [ok, setOk]               = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [uploading, setUploading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!userToken) return;
    setErr(null);
    setOk(false);
    setSubmitting(true);
    try {
      let finalCvUrl = cvUrl;
      if (cvFile) {
        setUploading(true);
        const upload = await apiUploadFile<{ file_url: string }>(`/files/upload`, cvFile, {
          token: userToken,
        });
        finalCvUrl = upload.file_url;
        setUploading(false);
      }

      await apiRequest(`/profile/create`, {
        method: "POST",
        token: userToken,
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastName,
          cv_url: finalCvUrl || null,
        }),
      });
      setOk(true);
      setCvFile(null);
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : "Could not save profile");
      setUploading(false);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div style={{ maxWidth: 680, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ marginBottom: "2rem" }}>
        <p className="section-label">Candidate onboarding</p>
        <h1 className="display" style={{ marginBottom: "0.4rem" }}>Profile baseline</h1>
        <p className="tagline" style={{ marginTop: "0.4rem" }}>
          Add your personal details so employers can understand who you are at a glance.
        </p>
      </div>

      {/* Stepper */}
      <div className="stepper" style={{ marginBottom: "2rem" }}>
        <div className="step done">
          <span className="step-num">✓</span>
          <span>Account</span>
        </div>
        <div className="step-connector" />
        <div className="step done">
          <span className="step-num">✓</span>
          <span>Verify</span>
        </div>
        <div className="step-connector" />
        <div className="step active">
          <span className="step-num">3</span>
          <span>Profile</span>
        </div>
        <div className="step-connector" />
        <div className="step">
          <span className="step-num">4</span>
          <span>Education</span>
        </div>
      </div>

      <div className="detail-shell">
        <div className="section-head">
          <div>
            <h2>Personal details</h2>
            <p className="section-head-sub">Used on your public candidate profile</p>
          </div>
        </div>

        <form className="form" onSubmit={onSubmit}>
          <div className="field-inline">
            <div className="field">
              <label htmlFor="fn">First name</label>
              <input
                id="fn"
                value={firstName}
                onChange={(ev) => setFirstName(ev.target.value)}
                placeholder="Jane"
                required
              />
            </div>
            <div className="field">
              <label htmlFor="ln">Last name</label>
              <input
                id="ln"
                value={lastName}
                onChange={(ev) => setLastName(ev.target.value)}
                placeholder="Smith"
                required
              />
            </div>
          </div>

          <div className="field">
            <label htmlFor="cv">
              CV / Resume URL or upload file{" "}
              <span style={{ color: "var(--text-faint)", fontSize: "0.75rem" }}>(optional)</span>
            </label>
            <input
              id="cv"
              type="url"
              value={cvUrl}
              onChange={(ev) => setCvUrl(ev.target.value)}
              placeholder="https://your-cv-link.pdf"
            />
          </div>

          <div className="field">
            <label htmlFor="cv-file">Upload CV / Resume</label>
            <input
              id="cv-file"
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              onChange={(ev) => setCvFile(ev.target.files?.[0] ?? null)}
            />
            {cvFile && (
              <div style={{ marginTop: "0.55rem", color: "var(--text-muted)", fontSize: "0.85rem" }}>
                Selected file: {cvFile.name}
              </div>
            )}
          </div>

          {err && <div className="alert alert-error">{err}</div>}
          {ok && (
            <div className="alert alert-success">
              ✓ Profile saved — continue to add your education history.
            </div>
          )}

          <div className="stack">
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? "Saving…" : "Save profile"}
            </button>
            <Link to="/onboarding/education" className="btn btn-secondary">
              Continue to education →
            </Link>
          </div>
        </form>
      </div>

      <p style={{ marginTop: "1.25rem", fontSize: "0.85rem", color: "var(--text-faint)", textAlign: "center" }}>
        <Link to="/dashboard">Skip for now — go to dashboard</Link>
      </p>
    </div>
  );
}
