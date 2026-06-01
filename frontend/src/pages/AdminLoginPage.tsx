import { FormEvent, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { apiRequest, ApiError } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function AdminLoginPage() {
  const { adminToken, setAdminToken } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr]           = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (adminToken) return <Navigate to="/admin/jobs" replace />;

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    setSubmitting(true);
    try {
      type R = { token?: string };
      const data = await apiRequest<R>(`/admin/login`, {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      if (!data.token) { setErr("Unexpected response shape"); return; }
      setAdminToken(data.token);
      navigate("/admin/jobs");
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : "Admin login failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-card-icon" style={{ background: "linear-gradient(135deg, #6366f1, #8b5cf6)", boxShadow: "0 8px 24px rgba(99,102,241,0.35)" }}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="3" width="7" height="7" rx="1" />
            <rect x="14" y="3" width="7" height="7" rx="1" />
            <rect x="3" y="14" width="7" height="7" rx="1" />
            <rect x="14" y="14" width="7" height="7" rx="1" />
          </svg>
        </div>
        <h1 className="auth-title">Employer console</h1>
        <p className="auth-subtitle">
          Sign in to manage your job postings and move candidates through the hiring pipeline.
        </p>

        <form className="form" onSubmit={onSubmit}>
          <div className="field">
            <label htmlFor="adm-email">Work email</label>
            <input
              id="adm-email"
              type="email"
              value={email}
              onChange={(ev) => setEmail(ev.target.value)}
              placeholder="admin@company.com"
              required
            />
          </div>
          <div className="field">
            <label htmlFor="adm-password">Password</label>
            <input
              id="adm-password"
              type="password"
              value={password}
              onChange={(ev) => setPassword(ev.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          {err && <div className="alert alert-error">{err}</div>}

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: "100%", justifyContent: "center", padding: "0.75rem", background: "linear-gradient(135deg, #6366f1, #8b5cf6)", boxShadow: "0 6px 20px rgba(99,102,241,0.3)" }}
            disabled={submitting}
          >
            {submitting ? "Signing in…" : "Enter admin workspace →"}
          </button>
        </form>

        <p className="auth-footer-link" style={{ marginTop: "1.25rem" }}>
          New employer?{" "}
          <Link to="/admin/register">Register an admin account</Link>
        </p>
        <p className="auth-footer-link" style={{ marginTop: "0.5rem" }}>
          <Link to="/" style={{ color: "var(--text-faint)", fontSize: "0.82rem" }}>← Job seeker homepage</Link>
        </p>
      </div>
    </div>
  );
}
