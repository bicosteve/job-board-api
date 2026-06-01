import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiRequest, ApiError, getApiBase } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { applicationStatusLabel, userStatusLabel } from "../lib/labels";

type Me = Record<string, unknown>;
type ProfileWrap = { profile?: Record<string, unknown> };
type Apps = { applications?: Record<string, unknown>[] };

export default function DashboardPage() {
  const { userToken } = useAuth();

  const [me, setMe] = useState<Me | null>(null);
  const [profile, setProfile] = useState<Record<string, unknown> | null>(null);
  const [applications, setApplications] = useState<Record<string, unknown>[]>([]);
  const [err, setErr] = useState<string[] | null>(null);
  const [liveConnected, setLiveConnected] = useState(false);

  useEffect(() => {
    if (!userToken) return;
    let cancelled = false;
    async function load() {
      const errors: string[] = [];
      try {
        const m = await apiRequest<Me>(`/user/me`, { method: "GET", token: userToken });
        if (!cancelled) setMe(m);
      } catch (e) {
        errors.push(e instanceof ApiError ? e.message : "Could not load /user/me");
      }
      try {
        const p = await apiRequest<ProfileWrap>(`/profile/get`, {
          method: "GET",
          token: userToken,
        });
        if (!cancelled) setProfile((p.profile as Record<string, unknown>) ?? null);
      } catch {
        errors.push(
          "Profile unavailable until you finish profile + education (backend joins education)."
        );
        if (!cancelled) setProfile(null);
      }
      try {
        const a = await apiRequest<Apps>(`/applications/user/list`, {
          method: "GET",
          token: userToken,
        });
        if (!cancelled) setApplications(Array.isArray(a.applications) ? a.applications : []);
      } catch (e) {
        errors.push(
          e instanceof ApiError ? e.message : "Could not load /applications/user/list"
        );
        if (!cancelled) setApplications([]);
      }
      if (!cancelled && errors.length) setErr(errors);
      else if (!cancelled) setErr(null);
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [userToken]);

  useEffect(() => {
    if (!userToken) return;
    const source = new EventSource(
      `${getApiBase()}/applications/user/stream?token=${encodeURIComponent(userToken)}`
    );

    source.onopen = () => setLiveConnected(true);
    source.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data) as Apps;
        if (Array.isArray(payload.applications)) {
          setApplications(payload.applications);
        }
      } catch {
        // ignore malformed event payloads
      }
    };
    source.onerror = () => {
      setLiveConnected(false);
      source.close();
    };

    return () => {
      source.close();
      setLiveConnected(false);
    };
  }, [userToken]);

  return (
    <>
      <div className="headline-row">
        <div>
          <h1 className="display">Dashboard</h1>
          <p className="tagline">
            Your personal snapshot with account details, profile information, and active
            applications.
          </p>
          {userToken && (
            <p style={{ color: liveConnected ? "var(--success)" : "var(--text-muted)", fontSize: "0.95rem", marginTop: "0.5rem" }}>
              Live status: {liveConnected ? "connected" : "reconnecting"}
            </p>
          )}
        </div>
      </div>

      {err && err.length > 0 && (
        <div style={{ marginBottom: "1rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          {err.map((line) => (
            <div key={line} className="alert alert-error">
              {line}
            </div>
          ))}
        </div>
      )}

      <section className="detail-shell section-spacer-bottom">
        <h2 style={{ fontSize: "1rem", marginBottom: "0.75rem" }}>Account</h2>
        {me ? (
          <dl
            style={{
              display: "grid",
              gridTemplateColumns: "auto 1fr",
              gap: "0.35rem 1rem",
              fontSize: "0.9rem",
            }}
          >
            {"email" in me && (
              <>
                <dt style={{ color: "var(--text-muted)" }}>Email</dt>
                <dd style={{ margin: 0 }}>{String(me.email)}</dd>
              </>
            )}
            {"user_id" in me && (
              <>
                <dt style={{ color: "var(--text-muted)" }}>Account ID</dt>
                <dd style={{ margin: 0 }}>{String(me.user_id)}</dd>
              </>
            )}
            {"status" in me && (
              <>
                <dt style={{ color: "var(--text-muted)" }}>Account status</dt>
                <dd style={{ margin: 0 }}>{userStatusLabel(me.status)}</dd>
              </>
            )}
          </dl>
        ) : (
          <p style={{ color: "var(--text-muted)" }}>Loading account…</p>
        )}
        <div className="stack" style={{ marginTop: "1rem" }}>
          <Link className="btn btn-secondary" to="/onboarding/profile">
            Profile
          </Link>
          <Link className="btn btn-secondary" to="/onboarding/education">
            Education
          </Link>
          <Link className="btn btn-primary" to="/">
            Find jobs
          </Link>
        </div>
      </section>

      <section className="detail-shell section-spacer-bottom">
        <h2 style={{ fontSize: "1rem", marginBottom: "0.75rem" }}>Profile snapshot</h2>
        {profile ? (
          <dl
            style={{
              display: "grid",
              gridTemplateColumns: "auto 1fr",
              gap: "0.35rem 1rem",
              fontSize: "0.9rem",
            }}
          >
            {Object.entries(profile).map(([k, v]) => (
              <div key={k} style={{ display: "contents" }}>
                <dt style={{ color: "var(--text-muted)", textTransform: "capitalize" }}>{k}</dt>
                <dd style={{ margin: 0 }}>{v == null ? "—" : String(v)}</dd>
              </div>
            ))}
          </dl>
        ) : (
          <p style={{ color: "var(--text-muted)" }}>
            Complete your profile and education sections to unlock your full candidate profile.
          </p>
        )}
      </section>

      <section className="detail-shell">
        <h2 style={{ fontSize: "1rem", marginBottom: "0.75rem" }}>My applications</h2>
        {applications.length === 0 ? (
          <p style={{ color: "var(--text-muted)" }}>No applications yet.</p>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Job</th>
                  <th>Status</th>
                  <th>Updated</th>
                </tr>
              </thead>
              <tbody>
                {applications.map((row) => (
                  <tr key={String(row.application_id ?? row.job_id ?? Math.random())}>
                    <td>{String(row.application_id ?? "—")}</td>
                    <td>
                      {row.job_id != null ? (
                        <Link to={`/jobs/${String(row.job_id)}`}>Job #{String(row.job_id)}</Link>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td>{applicationStatusLabel(Number(row.status))}</td>
                    <td style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>
                      {row.modified_at != null
                        ? String(row.modified_at)
                        : row.created_at != null
                          ? String(row.created_at)
                          : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}
