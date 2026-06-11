import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiRequest, ApiError, getApiBase } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { applicationStatusLabel, userStatusLabel } from "../lib/labels";

type Me = Record<string, unknown>;
type ProfileWrap = { profile?: Record<string, unknown> };
type Apps = { applications?: Record<string, unknown>[] };

function appStatusClass(status: number | string | undefined): string {
  const n = Number(status);
  if (n === 1) return "pill status-submitted";
  if (n === 2) return "pill status-review";
  if (n === 3) return "pill status-interview";
  if (n === 4) return "pill status-decision";
  return "pill pill-subtle";
}

export default function DashboardPage() {
  const { userToken } = useAuth();

  const [me, setMe] = useState<Me | null>(null);
  const [profile, setProfile] = useState<Record<string, unknown> | null>(null);
  const [applications, setApplications] = useState<Record<string, unknown>[]>([]);
  const [err, setErr] = useState<string[] | null>(null);
  const [liveConnected, setLiveConnected] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!userToken) return;
    let cancelled = false;
    async function load() {
      setLoading(true);
      const errors: string[] = [];
      try {
        const m = await apiRequest<Me>(`/user/me`, { method: "GET", token: userToken });
        if (!cancelled) setMe(m);
      } catch (e) {
        errors.push(e instanceof ApiError ? e.message : "Could not load account");
      }
      try {
        const p = await apiRequest<ProfileWrap>(`/profile/get`, { method: "GET", token: userToken });
        if (!cancelled) setProfile((p.profile as Record<string, unknown>) ?? null);
      } catch {
        if (!cancelled) setProfile(null);
      }
      try {
        const a = await apiRequest<Apps>(`/applications/user/list`, { method: "GET", token: userToken });
        if (!cancelled) setApplications(Array.isArray(a.applications) ? a.applications : []);
      } catch (e) {
        errors.push(e instanceof ApiError ? e.message : "Could not load applications");
        if (!cancelled) setApplications([]);
      }
      if (!cancelled) {
        if (errors.length) setErr(errors);
        else setErr(null);
        setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
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
        if (Array.isArray(payload.applications)) setApplications(payload.applications);
      } catch { /* ignore */ }
    };
    source.onerror = () => { setLiveConnected(false); source.close(); };
    return () => { source.close(); setLiveConnected(false); };
  }, [userToken]);

  const displayName = profile
    ? `${String(profile.first_name ?? "")} ${String(profile.last_name ?? "")}`.trim() || "Candidate"
    : me
    ? String(me.email ?? "").split("@")[0]
    : "—";

  const profileComplete = profile != null;

  const appsByStatus = applications.reduce<Record<number, number>>((acc, app) => {
    const s = Number(app.status ?? 1);
    acc[s] = (acc[s] ?? 0) + 1;
    return acc;
  }, {});

  return (
    <div className="dashboard-grid">
      {/* ── HEADER ── */}
      <div className="headline-row" style={{ marginBottom: "0.5rem" }}>
        <div>
          <p className="section-label">Candidate portal</p>
          <h1 className="display">
            {loading ? "Dashboard" : `Hello, ${displayName}`}
          </h1>
          <p className="tagline">
            Your personal snapshot — account details, profile status, and live applications.
          </p>
        </div>
        <div className="stack" style={{ alignSelf: "flex-end" }}>
          <span className={`live-indicator ${liveConnected ? "connected" : "reconnecting"}`}>
            <span className="live-dot" />
            {liveConnected ? "Live" : "Reconnecting"}
          </span>
          <Link to="/" className="btn btn-primary">Browse jobs →</Link>
        </div>
      </div>

      {err && err.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          {err.map((line) => (
            <div key={line} className="alert alert-warning">{line}</div>
          ))}
        </div>
      )}

      {/* ── STATS STRIP ── */}
      <div className="stats-strip">
        <div className="stat-card">
          <div className="stat-card-icon stat-card-icon-blue">📋</div>
          <div className="stat-card-value">{applications.length}</div>
          <div className="stat-card-label">Total applications</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-icon stat-card-icon-purple">🔍</div>
          <div className="stat-card-value">{appsByStatus[2] ?? 0}</div>
          <div className="stat-card-label">In review</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-icon stat-card-icon-green">🤝</div>
          <div className="stat-card-value">{appsByStatus[3] ?? 0}</div>
          <div className="stat-card-label">Interviews</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-icon stat-card-icon-orange">
            {profileComplete ? "✓" : "○"}
          </div>
          <div className="stat-card-value">{profileComplete ? "Done" : "—"}</div>
          <div className="stat-card-label">Profile status</div>
        </div>
      </div>

      {/* ── ACCOUNT + PROFILE ── */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1.25rem" }}>
        {/* Account */}
        <section className="detail-shell">
          <div className="section-head">
            <div>
              <h2>Account details</h2>
              <p className="section-head-sub">Your login and verification status</p>
            </div>
            <div className="stack">
              <Link className="btn btn-secondary" style={{ fontSize: "0.82rem", padding: "0.4rem 0.8rem" }} to="/onboarding/profile">
                Edit profile
              </Link>
            </div>
          </div>

          {me ? (
            <dl className="dl-grid">
              {"email" in me && (
                <>
                  <dt>Email</dt>
                  <dd>{String(me.email)}</dd>
                </>
              )}
              {"user_id" in me && (
                <>
                  <dt>Account ID</dt>
                  <dd style={{ fontFamily: "monospace", fontSize: "0.85rem" }}>#{String(me.user_id)}</dd>
                </>
              )}
              {"status" in me && (
                <>
                  <dt>Status</dt>
                  <dd>
                    <span className={`pill ${Number(me.status) === 1 ? "status-open" : "pill-subtle"}`}>
                      {userStatusLabel(me.status as never)}
                    </span>
                  </dd>
                </>
              )}
            </dl>
          ) : (
            <div className="skeleton-line" style={{ width: "70%", height: 16 }} />
          )}

          <div className="stack" style={{ marginTop: "1.25rem" }}>
            <Link className="btn btn-secondary" to="/onboarding/education">Education</Link>
          </div>
        </section>

        {/* Profile snapshot */}
        <section className="detail-shell">
          <div className="section-head">
            <div>
              <h2>Profile snapshot</h2>
              <p className="section-head-sub">Your public candidate details</p>
            </div>
            {!profileComplete && (
              <Link to="/onboarding/profile" className="btn btn-primary" style={{ fontSize: "0.82rem", padding: "0.4rem 0.9rem" }}>
                Complete →
              </Link>
            )}
          </div>

          {profileComplete ? (
            <dl className="dl-grid">
              {Object.entries(profile!).map(([k, v]) => (
                <div key={k} style={{ display: "contents" }}>
                  <dt style={{ textTransform: "capitalize" }}>{k.replace(/_/g, " ")}</dt>
                  <dd>
                    {k.toLowerCase().includes("url") && typeof v === "string" && v ? (
                      <a href={v} target="_blank" rel="noreferrer" style={{ fontSize: "0.85rem" }}>
                        View CV ↗
                      </a>
                    ) : (
                      v == null ? "—" : String(v)
                    )}
                  </dd>
                </div>
              ))}
            </dl>
          ) : (
            <div style={{ padding: "1.5rem 0", textAlign: "center" }}>
              <p style={{ color: "var(--text-muted)", margin: "0 0 1rem", fontSize: "0.92rem" }}>
                Complete your profile and education to unlock your full candidate card.
              </p>
              <div className="stack" style={{ justifyContent: "center" }}>
                <Link to="/onboarding/profile" className="btn btn-primary">Add profile</Link>
                <Link to="/onboarding/education" className="btn btn-secondary">Add education</Link>
              </div>
            </div>
          )}
        </section>
      </div>

      {/* ── APPLICATIONS ── */}
      <section className="detail-shell">
        <div className="section-head">
          <div>
            <h2>My applications</h2>
            <p className="section-head-sub">
              {applications.length} application{applications.length === 1 ? "" : "s"} submitted
            </p>
          </div>
          <Link to="/" className="btn btn-secondary" style={{ fontSize: "0.82rem", padding: "0.4rem 0.8rem" }}>
            Find more roles
          </Link>
        </div>

        {applications.length === 0 ? (
          <div style={{ padding: "2rem 1rem", textAlign: "center" }}>
            <p style={{ margin: "0 0 0.5rem", fontWeight: 600, fontSize: "1.05rem" }}>No applications yet</p>
            <p style={{ color: "var(--text-muted)", margin: "0 0 1.25rem", fontSize: "0.9rem" }}>
              Browse open roles and submit your first application to get started.
            </p>
            <Link to="/" className="btn btn-primary">Browse open roles →</Link>
          </div>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Position</th>
                  <th>Status</th>
                  <th>Last updated</th>
                </tr>
              </thead>
              <tbody>
                {applications.map((row) => {
                  const id = String(row.application_id ?? "—");
                  const updated = row.modified_at != null
                    ? String(row.modified_at)
                    : row.created_at != null
                    ? String(row.created_at)
                    : "—";
                  return (
                    <tr key={String(row.application_id ?? row.job_id ?? Math.random())}>
                      <td style={{ fontFamily: "monospace", fontSize: "0.82rem", color: "var(--text-faint)" }}>
                        {id}
                      </td>
                      <td>
                        {row.job_id != null ? (
                          <Link to={`/jobs/${String(row.job_id)}`} style={{ fontWeight: 500 }}>
                            Job #{String(row.job_id)}
                          </Link>
                        ) : "—"}
                      </td>
                      <td>
                        <span className={appStatusClass(row.status as number)}>
                          {applicationStatusLabel(Number(row.status))}
                        </span>
                      </td>
                      <td style={{ color: "var(--text-faint)", fontSize: "0.82rem" }}>{updated}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
