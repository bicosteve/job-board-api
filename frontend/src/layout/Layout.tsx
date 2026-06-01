import { Link, NavLink, Outlet } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import { apiRequest } from "../api/client";
import { useAuth } from "../context/AuthContext";

const footerSections = [
  {
    title: "Platform",
    links: [
      { label: "Jobs", to: "/" },
      { label: "Dashboard", to: "/dashboard" },
      { label: "Admin console", to: "/admin/jobs" },
    ],
  },
  {
    title: "Account",
    links: [
      { label: "Register", to: "/register" },
      { label: "Sign in", to: "/login" },
      { label: "Verify account", to: "/verify" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About OpenHire", to: "/" },
      { label: "Employer hub", to: "/admin/login" },
    ],
  },
];

const healthStatus = {
  ok: { label: "Live", tone: "online" },
  down: { label: "Offline", tone: "offline" },
  unknown: { label: "Checking", tone: "pending" },
} as const;

export default function Layout() {
  const { userToken, adminToken, logoutUser, logoutAdmin } = useAuth();
  const [health, setHealth] = useState<"ok" | "down" | "unknown">("unknown");
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    if (typeof window === "undefined") return "light";
    const saved = window.localStorage.getItem("jobboard_theme");
    return saved === "dark" ? "dark" : "light";
  });

  const navItems = useMemo(
    () => [
      { label: "Jobs", to: "/" },
      ...(userToken ? [{ label: "Dashboard", to: "/dashboard" }] : []),
      ...(userToken
        ? [
            { label: "Profile", to: "/onboarding/profile" },
            { label: "Education", to: "/onboarding/education" },
          ]
        : []),
      { label: "Employers", to: "/admin/login" },
    ],
    [userToken]
  );

  useEffect(() => {
    let cancelled = false;

    async function ping() {
      try {
        await apiRequest(`/health/check`, { method: "GET", headers: {} });
        if (!cancelled) setHealth("ok");
      } catch {
        if (!cancelled) setHealth("down");
      }
    }

    ping();
    const intervalId = window.setInterval(ping, 45000);
    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
    };
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    window.localStorage.setItem("jobboard_theme", theme);
  }, [theme]);

  const { label: healthLabel, tone: healthTone } = healthStatus[health];

  return (
    <>
      <header className="header">
        <div className="header-inner">
          <div className="brand-group">
            <Link to="/" className="logo">
              Open<span className="logo-accent">Hire</span>
            </Link>
            <span className={`badge-online badge-${healthTone}`}>
              <span className="badge-online-dot"></span>
              {healthLabel}
            </span>
          </div>

          <nav className="nav-links" aria-label="Primary navigation">
            {navItems.map((item) => (
              <NavLink key={item.to} to={item.to} end={item.to === "/"}>
                {item.label}
              </NavLink>
            ))}

            <button
              type="button"
              className="btn btn-ghost theme-toggle"
              onClick={() => setTheme((prev) => (prev === "light" ? "dark" : "light"))}
              aria-label="Toggle color theme"
            >
              {theme === "light" ? "Dark mode" : "Light mode"}
            </button>

            {userToken ? (
              <button type="button" className="btn btn-secondary" onClick={logoutUser}>
                Sign out
              </button>
            ) : (
              <>
                <NavLink to="/login">Sign in</NavLink>
                <Link to="/register" className="btn btn-primary">
                  Join
                </Link>
              </>
            )}

            {adminToken && (
              <div className="nav-admin-actions">
                <NavLink to="/admin/jobs">Admin</NavLink>
                <button type="button" className="btn btn-ghost" onClick={logoutAdmin}>
                  Exit admin
                </button>
              </div>
            )}
          </nav>
        </div>
      </header>

      <main className="page">
        <Outlet />
      </main>

      <footer className="footer">
        <div className="footer-inner">
          <div className="footer-brand">
            <Link to="/" className="logo">
              Open<span className="logo-accent">Hire</span>
            </Link>
            <p>
              A modern hiring platform with clean pipelines, real-time updates, and a
              polished application experience.
            </p>
          </div>

          {footerSections.map((section) => (
            <div key={section.title} className="footer-col">
              <h4>{section.title}</h4>
              {section.links.map((link) => (
                <Link key={link.to} to={link.to}>
                  {link.label}
                </Link>
              ))}
            </div>
          ))}
        </div>

        <div className="footer-bottom">
          <span>OpenHire · Designed for high-trust hiring journeys</span>
          <span>API status: {healthLabel}</span>
        </div>
      </footer>
    </>
  );
}
