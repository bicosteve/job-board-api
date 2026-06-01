import { FormEvent, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { apiRequest, ApiError } from "../api/client";

type LocationState = { email?: string; verification_code_hint?: string };

export default function VerifyPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const st = location.state as LocationState | null;

  const [email, setEmail] = useState(st?.email ?? "");
  const [code, setCode] = useState(st?.verification_code_hint ?? "");
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    setMsg(null);
    setSubmitting(true);
    try {
      await apiRequest(`/user/verify`, {
        method: "POST",
        body: JSON.stringify({ email, verification_code: code }),
      });
      setMsg("Account verified. You can sign in.");
      navigate("/login", {
        replace: true,
        state: { verified: true },
      });
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : "Verification failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <div className="headline-row">
        <div className="form-shell">
          <h1 className="display">Confirm your inbox</h1>
          <p className="tagline">
            Enter the verification code sent after registration to activate your account.
          </p>
        </div>
      </div>
      <div className="detail-shell form-shell">
      <form className="form form-centered" onSubmit={onSubmit}>
        <div className="field">
          <label htmlFor="verify-email">Email</label>
          <input
            id="verify-email"
            type="email"
            value={email}
            onChange={(ev) => setEmail(ev.target.value)}
            required
          />
        </div>
        <div className="field">
          <label htmlFor="verify-code">Verification code</label>
          <input
            id="verify-code"
            value={code}
            onChange={(ev) => setCode(ev.target.value)}
            required
            autoComplete="one-time-code"
          />
        </div>
        {err && <div className="alert alert-error">{err}</div>}
        {msg && <div className="alert alert-success">{msg}</div>}
        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? "Verifying…" : "Verify account"}
        </button>
        <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
          Wrong place?{" "}
          <Link to="/register" style={{ color: "var(--accent)" }}>
            Register again
          </Link>
        </p>
      </form>
      </div>
    </>
  );
}
