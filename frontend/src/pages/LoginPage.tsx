import { FormEvent, useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { apiRequest, ApiError } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const { setUserToken } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: string } | null)?.from ?? "/dashboard";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    setSubmitting(true);
    try {
      type R = { token?: string };
      const data = await apiRequest<R>(`/user/login`, {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      const token = data.token;
      if (!token) {
        setErr("No token in response");
        return;
      }
      setUserToken(token);
      navigate(from, { replace: true });
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <div className="headline-row">
        <div className="form-shell">
          <h1 className="display">Welcome back</h1>
          <p className="tagline">
            Verified accounts only finish email verification before signing in.
          </p>
        </div>
      </div>
      <div className="detail-shell form-shell">
      <form className="form form-centered" onSubmit={onSubmit}>
        <div className="field">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="field">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {err && <div className="alert alert-error">{err}</div>}
        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? "Signing in…" : "Sign in"}
        </button>
        <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
          New here?{" "}
          <Link to="/register" style={{ color: "var(--accent)" }}>
            Create an account
          </Link>
        </p>
      </form>
      </div>
    </>
  );
}
