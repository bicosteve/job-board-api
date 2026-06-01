import { FormEvent, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { apiRequest, ApiError } from "../api/client";

type LocationState = { email?: string; verification_code_hint?: string };

export default function VerifyPage() {
  const location = useLocation();
  const navigate  = useNavigate();
  const st = location.state as LocationState | null;

  const [email, setEmail] = useState(st?.email ?? "");
  const [code, setCode]   = useState(st?.verification_code_hint ?? "");
  const [msg, setMsg]     = useState<string | null>(null);
  const [err, setErr]     = useState<string | null>(null);
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
      setMsg("Account verified successfully.");
      setTimeout(() => navigate("/login", { replace: true, state: { verified: true } }), 1200);
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : "Verification failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-card-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="20 6 9 17 4 12" />
          </svg>
        </div>
        <h1 className="auth-title">Verify your email</h1>
        <p className="auth-subtitle">
          Enter the verification code sent to your inbox after registration.
        </p>

        {/* Progress steps */}
        <div className="stepper" style={{ marginBottom: "1.5rem" }}>
          <div className="step done">
            <span className="step-num">✓</span>
            <span>Account</span>
          </div>
          <div className="step-connector" />
          <div className="step active">
            <span className="step-num">2</span>
            <span>Verify</span>
          </div>
          <div className="step-connector" />
          <div className="step">
            <span className="step-num">3</span>
            <span>Profile</span>
          </div>
        </div>

        <form className="form" onSubmit={onSubmit}>
          <div className="field">
            <label htmlFor="verify-email">Email address</label>
            <input
              id="verify-email"
              type="email"
              value={email}
              onChange={(ev) => setEmail(ev.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>
          <div className="field">
            <label htmlFor="verify-code">Verification code</label>
            <input
              id="verify-code"
              value={code}
              onChange={(ev) => setCode(ev.target.value)}
              placeholder="Paste your code here"
              required
              autoComplete="one-time-code"
              style={{ letterSpacing: code.length > 4 ? "0.12em" : "normal", fontFamily: "monospace" }}
            />
          </div>

          {err && <div className="alert alert-error">{err}</div>}
          {msg && <div className="alert alert-success">✓ {msg} Redirecting…</div>}

          <button type="submit" className="btn btn-primary" style={{ width: "100%", justifyContent: "center", padding: "0.75rem" }} disabled={submitting || !!msg}>
            {submitting ? "Verifying…" : "Verify account →"}
          </button>
        </form>

        <p className="auth-footer-link" style={{ marginTop: "1.25rem" }}>
          Need a new account?{" "}
          <Link to="/register">Register again</Link>
        </p>
      </div>
    </div>
  );
}
