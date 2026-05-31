import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiRequest, ApiError } from "../api/client";

export default function RegisterPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
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
    }
  }

  return (
    <>
      <div className="headline-row">
        <div className="form-shell">
          <h1 className="display">Create your seeker profile</h1>
          <p className="tagline">
            Create your account in under a minute, then confirm your email to continue.
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
            value={email}
            onChange={(ev) => setEmail(ev.target.value)}
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
            required
          />
        </div>
        {err && <div className="alert alert-error">{err}</div>}
        <button type="submit" className="btn btn-primary">
          Continue
        </button>
        <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
          Already registered?{" "}
          <Link to="/login" style={{ color: "var(--accent)" }}>
            Sign in
          </Link>
        </p>
      </form>
      </div>
    </>
  );
}
