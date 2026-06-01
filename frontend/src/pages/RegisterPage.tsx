import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiRequest, ApiError } from "../api/client";

export default function RegisterPage() {
  const navigate = useNavigate();
  const [email, setEmail]                   = useState("");
  const [password, setPassword]             = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [err, setErr]                       = useState<string | null>(null);
  const [submitting, setSubmitting]         = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    setSubmitting(true);
    try {
      type R = { verification_code?: string };
      const res = await apiRequest<R>(`/user/register`, {
        method: "POST",
        body: JSON.stringify({ email, password, confirm_password: confirmPassword }),
      });
      navigate(`/verify`, {
        state: {
          email,
          verification_code_hint:
            typeof res.verification_code === "string" ? res.verification_code : undefined,
        },
      });
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : "Registration failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-card-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <line x1="19" y1="8" x2="19" y2="14" />
            <line x1="22" y1="11" x2="16" y2="11" />
          </svg>
        </div>
        <h1 className="auth-title">Create your account</h1>
        <p className="auth-subtitle">
          Join OpenHire in under a minute — confirm your email to start applying.
        </p>

        {/* Progress steps */}
        <div className="stepper" style={{ marginBottom: "1.5rem" }}>
          <div className="step active">
            <span className="step-num">1</span>
            <span>Account</span>
          </div>
          <div className="step-connector" />
          <div className="step">
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
            <label htmlFor="email">Email address</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(ev) => setEmail(ev.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(ev) => setPassword(ev.target.value)}
              placeholder="••••••••"
              required
            />
          </div>
          <div className="field">
            <label htmlFor="confirm_password">Confirm password</label>
            <input
              id="confirm_password"
              type="password"
              value={confirmPassword}
              onChange={(ev) => setConfirmPassword(ev.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          {err && <div className="alert alert-error">{err}</div>}

          <button type="submit" className="btn btn-primary" style={{ width: "100%", justifyContent: "center", padding: "0.75rem" }} disabled={submitting}>
            {submitting ? "Creating account…" : "Create account →"}
          </button>
        </form>

        <p className="auth-footer-link" style={{ marginTop: "1.25rem" }}>
          Already registered?{" "}
          <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
