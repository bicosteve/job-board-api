import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { apiRequest, ApiError } from "../api/client";
import { useAuth } from "../context/AuthContext";

const LEVELS = ["Secondary", "University", "Certificates"] as const;

export default function EducationOnboardingPage() {
  const { userToken } = useAuth();
  const [level, setLevel] = useState<string>(LEVELS[1]);
  const [institution, setInstitution] = useState("");
  const [field, setField] = useState("");
  /** dd-MM-yyyy per API */
  const [startDate, setStartDate] = useState("01-01-2018");
  const [endDate, setEndDate] = useState("ongoing");
  const [description, setDescription] = useState("");

  const [err, setErr] = useState<string | null>(null);
  const [ok, setOk] = useState(false);
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
    <>
      <div className="headline-row">
        <div className="form-shell">
          <h1 className="display">Education record</h1>
          <p className="tagline">
            Add your strongest education experience to complete your profile.
          </p>
        </div>
      </div>
      <div className="detail-shell form-shell">
      <form className="form form-centered form-wide" onSubmit={onSubmit}>
        <div className="field">
          <label htmlFor="level">Level</label>
          <select id="level" value={level} onChange={(ev) => setLevel(ev.target.value)}>
            {LEVELS.map((l) => (
              <option key={l} value={l}>
                {l}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="inst">Institution</label>
          <input
            id="inst"
            value={institution}
            onChange={(ev) => setInstitution(ev.target.value)}
            required
            minLength={3}
          />
        </div>
        <div className="field">
          <label htmlFor="field">Field (optional)</label>
          <input id="field" value={field} onChange={(ev) => setField(ev.target.value)} />
        </div>
        <div className="field-inline">
          <div className="field">
            <label htmlFor="sd">Start (dd-MM-yyyy)</label>
            <input id="sd" value={startDate} onChange={(ev) => setStartDate(ev.target.value)} required />
          </div>
          <div className="field">
            <label htmlFor="ed">End (dd-MM-yyyy or ongoing)</label>
            <input id="ed" value={endDate} onChange={(ev) => setEndDate(ev.target.value)} required />
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
          />
        </div>
        {err && <div className="alert alert-error">{err}</div>}
        {ok && (
          <div className="alert alert-success">
            Education saved. You can now view your profile on the dashboard.
          </div>
        )}
        <div className="stack">
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? "Saving…" : "Save education"}
          </button>
          <Link to="/dashboard">Go to dashboard</Link>
        </div>
      </form>
      </div>
    </>
  );
}
