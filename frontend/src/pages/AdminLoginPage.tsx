import { FormEvent, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { apiRequest, ApiError } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function AdminLoginPage() {
  const { adminToken, setAdminToken } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);

  if (adminToken) {
    return <Navigate to="/admin/jobs" replace />;
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    try {
      type R = { token?: string };
      const data = await apiRequest<R>(`/admin/login`, {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      if (!data.token) {
        setErr("Unexpected response shape");
        return;
      }
      setAdminToken(data.token);
      navigate("/admin/jobs");
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : "Admin login failed");
    }
  }

  return (
    <>
      <div className="headline-row">
        <div className="form-shell">
          <h1 className="display">Employer console</h1>
          <p className="tagline">
            Sign in to manage postings and candidate pipelines from one workspace.
          </p>
        </div>
      </div>
      <div className="detail-shell form-shell">
      <form className="form form-centered" onSubmit={onSubmit}>
        <div className="field">
          <label htmlFor="adm-email">Work email</label>
          <input
            id="adm-email"
            type="email"
            value={email}
            onChange={(ev) => setEmail(ev.target.value)}
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
            required
          />
        </div>
        {err && <div className="alert alert-error">{err}</div>}
        <button type="submit" className="btn btn-primary">
          Enter admin workspace
        </button>
        <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
          Bootstrap a new moderator?{" "}
          <Link to="/admin/register" style={{ color: "var(--accent)" }}>
            Register admin
          </Link>
        </p>
        <Link to="/" style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
          ← Job seeker homepage
        </Link>
      </form>
      </div>
    </>
  );
}
