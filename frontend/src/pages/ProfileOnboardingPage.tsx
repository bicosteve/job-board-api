import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { apiRequest, ApiError } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function ProfileOnboardingPage() {
  const { userToken } = useAuth();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [cvUrl, setCvUrl] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [ok, setOk] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!userToken) return;
    setErr(null);
    setOk(false);
    try {
      await apiRequest(`/profile/create`, {
        method: "POST",
        token: userToken,
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastName,
          cv_url: cvUrl || null,
        }),
      });
      setOk(true);
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : "Could not save profile");
    }
  }

  return (
    <>
      <div className="headline-row">
        <div className="form-shell">
          <h1 className="display">Profile baseline</h1>
          <p className="tagline">
            Add your personal details so recruiters can understand your profile quickly.
          </p>
        </div>
      </div>
      <div className="detail-shell form-shell">
      <form className="form form-centered" onSubmit={onSubmit}>
        <div className="field-inline">
          <div className="field">
            <label htmlFor="fn">First name</label>
            <input id="fn" value={firstName} onChange={(ev) => setFirstName(ev.target.value)} required />
          </div>
          <div className="field">
            <label htmlFor="ln">Last name</label>
            <input id="ln" value={lastName} onChange={(ev) => setLastName(ev.target.value)} required />
          </div>
        </div>
        <div className="field">
          <label htmlFor="cv">CV URL (optional)</label>
          <input id="cv" type="url" value={cvUrl} onChange={(ev) => setCvUrl(ev.target.value)} />
        </div>
        {err && <div className="alert alert-error">{err}</div>}
        {ok && (
          <div className="alert alert-success">
            Saved. Next step: add your education details.
          </div>
        )}
        <button type="submit" className="btn btn-primary">
          Save profile
        </button>
        <Link
          to="/onboarding/education"
          className="btn btn-secondary"
          style={{ textAlign: "center" }}
        >
          Continue to education
        </Link>
      </form>
      </div>
    </>
  );
}
