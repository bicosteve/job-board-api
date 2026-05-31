import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiRequest, ApiError } from "../api/client";

export default function RegisterAdminPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [codeHint, setCodeHint] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    setCodeHint(null);
    try {
      type R = { verification_code?: string };
      const res = await apiRequest<R>(`/admin/register`, {
        method: "POST",
        body: JSON.stringify({ email, password, confirm_password: confirmPassword }),
      });
      if (typeof res.verification_code === "string") setCodeHint(res.verification_code);
    } catch (err0) {
      setErr(err0 instanceof ApiError ? err0.message : "Admin register failed");
    }
  }

  async function verify(e: FormEvent) {
    e.preventDefault();
    if (!codeHint) return;
    setErr(null);
    try {
      await apiRequest(`/admin/verify`, {
        method: "POST",
        body: JSON.stringify({ email, verification_code: codeHint }),
      });
      navigate("/admin/login", {
        replace: true,
        state: { banner: "Admin verified — sign in." },
      });
    } catch (err0) {
      setErr(err0 instanceof ApiError ? err0.message : "Verification failed");
    }
  }

  return (
    <>
      <div className="headline-row">
        <div className="form-shell">
          <h1 className="display">Register admin</h1>
          <p className="tagline">
            Create an employer account, then confirm the verification code to activate access.
          </p>
        </div>
      </div>
      <div className="detail-shell form-shell">
      <form className="form form-centered" onSubmit={onSubmit}>
        <div className="field">
          <label>Email</label>
          <input type="email" value={email} onChange={(ev) => setEmail(ev.target.value)} required />
        </div>
        <div className="field">
          <label>Password (max 20 per schema)</label>
          <input
            type="password"
            value={password}
            onChange={(ev) => setPassword(ev.target.value)}
            required
          />
        </div>
        <div className="field">
          <label>Confirm</label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(ev) => setConfirmPassword(ev.target.value)}
            required
          />
        </div>
        {err && <div className="alert alert-error">{err}</div>}
        {codeHint && (
          <div className="alert alert-success">
            Verification code:{" "}
            <strong style={{ letterSpacing: "0.06em" }}>{codeHint}</strong>
          </div>
        )}
        <button type="submit" className="btn btn-secondary">
          Create admin
        </button>
      </form>
      {codeHint && (
        <form className="form form-centered" style={{ marginTop: "1.5rem" }} onSubmit={verify}>
          <button type="submit" className="btn btn-primary">
            Verify and continue ({email})
          </button>
        </form>
      )}
      </div>
      <p style={{ marginTop: "2rem", fontSize: "0.9rem" }}>
        <Link to="/admin/login">Back to employer login</Link>
      </p>
    </>
  );
}
