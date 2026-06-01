import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiRequest, ApiError } from "../api/client";

export default function RegisterAdminPage() {
  const navigate = useNavigate();
  const [email, setEmail]                   = useState("");
  const [password, setPassword]             = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [err, setErr]                       = useState<string | null>(null);
  const [codeHint, setCodeHint]             = useState<string | null>(null);
  const [creating, setCreating]             = useState(false);
  const [verifying, setVerifying]           = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    setCodeHint(null);
    setCreating(true);
    try {
      type R = { verification_code?: string };
      const res = await apiRequest<R>(`/admin/register`, {
        method: "POST",
        body: JSON.stringify({ email, password, confirm_password: confirmPassword }),
      });
      if (typeof res.verification_code === "string") setCodeHint(res.verification_code);
    } catch (err0) {
      setErr(err0 instanceof ApiError ? err0.message : "Admin register failed");
    } finally {
      setCreating(false);
    }
  }

  async function verify(e: FormEvent) {
    e.preventDefault();
    if (!codeHint) return;
    setErr(null);
    setVerifying(true);
    try {
      await apiRequest(`/admin/verify`, {
        method: "POST",
        body: JSON.stringify({ email, verification_code: codeHint }),
      });
      navigate("/admin/login", { replace: true, state: { banner: "Admin verified — sign in." } });
    } catch (err0) {
      setErr(err0 instanceof ApiError ? err0.message : "Verification failed");
    } finally {
      setVerifying(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-card-icon" style={{ background: "linear-gradient(135deg, #6366f1, #8b5cf6)", boxShadow: "0 8px 24px rgba(99,102,241,0.35)" }}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M23 21v-2a4 4 0 00-3-3.87" />
            <path d="M16 3.13a4 4 0 010 7.75" />
          </svg>
        </div>
        <h1 className="auth-title">Register employer</h1>
        <p className="auth-subtitle">
          Create an employer account to post jobs and manage your hiring pipeline.
        </p>

        {!codeHint ? (
          <form className="form" onSubmit={onSubmit}>
            <div className="field">
              <label>Work email</label>
              <input
                type="email"
                value={email}
                onChange={(ev) => setEmail(ev.target.value)}
                placeholder="admin@company.com"
                required
              />
            </div>
            <div className="field">
              <label>
                Password{" "}
                <span style={{ color: "var(--text-faint)", fontSize: "0.75rem" }}>(max 20 chars)</span>
              </label>
              <input
                type="password"
                value={password}
                onChange={(ev) => setPassword(ev.target.value)}
                placeholder="••••••••"
                required
              />
            </div>
            <div className="field">
              <label>Confirm password</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(ev) => setConfirmPassword(ev.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            {err && <div className="alert alert-error">{err}</div>}

            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: "100%", justifyContent: "center", padding: "0.75rem", background: "linear-gradient(135deg, #6366f1, #8b5cf6)", boxShadow: "0 6px 20px rgba(99,102,241,0.3)" }}
              disabled={creating}
            >
              {creating ? "Creating account…" : "Create employer account →"}
            </button>
          </form>
        ) : (
          <div>
            <div className="alert alert-success" style={{ marginBottom: "1.25rem" }}>
              <span>✓</span>
              <div>
                <strong>Account created!</strong>
                <p style={{ margin: "0.3rem 0 0", fontSize: "0.85rem" }}>
                  Your verification code:{" "}
                  <code style={{ fontFamily: "monospace", fontWeight: 700, letterSpacing: "0.12em", fontSize: "0.95rem" }}>
                    {codeHint}
                  </code>
                </p>
              </div>
            </div>

            <form className="form" onSubmit={verify}>
              {err && <div className="alert alert-error">{err}</div>}
              <button
                type="submit"
                className="btn btn-primary"
                style={{ width: "100%", justifyContent: "center", padding: "0.75rem", background: "linear-gradient(135deg, #6366f1, #8b5cf6)", boxShadow: "0 6px 20px rgba(99,102,241,0.3)" }}
                disabled={verifying}
              >
                {verifying ? "Verifying…" : `Verify & continue as ${email} →`}
              </button>
            </form>
          </div>
        )}

        <p className="auth-footer-link" style={{ marginTop: "1.25rem" }}>
          Already have an account?{" "}
          <Link to="/admin/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
