import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { apiRequest, ApiError } from "../api/client";
import { useAuth } from "../context/AuthContext";

const LEVELS = ["Secondary", "University", "Certificates"] as const;

export default function EducationOnboardingPage() {
  const { userToken } = useAuth();
  const [level, setLevel]           = useState<string>(LEVELS[1]);
  const [institution, setInstitution] = useState("");
  const [field, setField]           = useState("");
  const [startDate, setStartDate]   = useState("01-01-2018");
  const [endDate, setEndDate]       = useState("ongoing");
  const [description, setDescription] = useState("");

  const [err, setErr]               = useState<string | null>(null);
  const [ok, setOk]                 = useState(false);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!userToken) return;
    setErr(null);
    setOk(false);
    setSubmitting(true);
    try {
      await apiRequest(`/education/create`, {
        method: "POST",
        token: userToken,
        body: JSON.stringify({
          level,
          institution,
          field: field || null,
          start_date: startDate,
          end_date: endDate,
          description,
        }),
      });
      setOk(true);
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : "Education create failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div style={{ maxWidth: 680, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ marginBottom: "2rem" }}>
        <p className="section-label">Candidate onboarding</p>
        <h1 className="display" style={{ marginBottom: "0.4rem" }}>Education record</h1>
        <p className="tagline" style={{ marginTop: "0.4rem" }}>
          Add your strongest education experience to complete your candidate profile.
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
        <div className="step done">
          <span className="step-num">✓</span>
          <span>Profile</span>
        </div>
        <div className="step-connector" />
        <div className="step active">
          <span className="step-num">4</span>
          <span>Education</span>
        </div>
      </div>

      <div className="detail-shell">
        <div className="section-head">
          <div>
            <h2>Education history</h2>
            <p className="section-head-sub">Dates use dd-MM-yyyy format, or type "ongoing"</p>
          </div>
        </div>

        <form className="form" onSubmit={onSubmit}>
          <div className="field-inline">
            <div className="field">
              <label htmlFor="level">Education level</label>
              <select id="level" value={level} onChange={(ev) => setLevel(ev.target.value)}>
                {LEVELS.map((l) => <option key={l} value={l}>{l}</option>)}
              </select>
            </div>
            <div className="field">
              <label htmlFor="field">
                Field of study{" "}
                <span style={{ color: "var(--text-faint)", fontSize: "0.75rem" }}>(optional)</span>
              </label>
              <input
                id="field"
                value={field}
                onChange={(ev) => setField(ev.target.value)}
                placeholder="e.g. Computer Science"
              />
            </div>
          </div>

          <div className="field">
            <label htmlFor="inst">Institution name</label>
            <input
              id="inst"
              value={institution}
              onChange={(ev) => setInstitution(ev.target.value)}
              placeholder="e.g. MIT, Stanford, Coursera"
              required
              minLength={3}
            />
          </div>

          <div className="field-inline">
            <div className="field">
              <label htmlFor="sd">Start date <span style={{ color: "var(--text-faint)", fontSize: "0.72rem" }}>(dd-MM-yyyy)</span></label>
              <input
                id="sd"
                value={startDate}
                onChange={(ev) => setStartDate(ev.target.value)}
                placeholder="01-09-2018"
                required
              />
            </div>
            <div className="field">
              <label htmlFor="ed">End date <span style={{ color: "var(--text-faint)", fontSize: "0.72rem" }}>(dd-MM-yyyy or ongoing)</span></label>
              <input
                id="ed"
                value={endDate}
                onChange={(ev) => setEndDate(ev.target.value)}
                placeholder="01-06-2022 or ongoing"
                required
              />
            </div>
          </div>

          <div className="field">
            <label htmlFor="desc">Description</label>
            <textarea
              id="desc"
              value={description}
              onChange={(ev) => setDescription(ev.target.value)}
              required
              minLength={2}
              rows={4}
              placeholder="Briefly describe your studies, key subjects, or achievements…"
            />
          </div>

          {err && <div className="alert alert-error">{err}</div>}
          {ok && (
            <div className="alert alert-success">
              ✓ Education saved — your candidate profile is now complete!
            </div>
          )}

          <div className="stack">
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? "Saving…" : "Save education"}
            </button>
            {ok && (
              <Link to="/dashboard" className="btn btn-secondary">Go to dashboard →</Link>
            )}
          </div>
        </form>
      </div>

      <p style={{ marginTop: "1.25rem", fontSize: "0.85rem", color: "var(--text-faint)", textAlign: "center" }}>
        <Link to="/dashboard">Skip for now — go to dashboard</Link>
      </p>
    </div>
  );
}
