import { Link, NavLink, Outlet } from "react-router-dom";
import { useEffect, useState } from "react";
import { apiRequest, getApiBase } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function Layout() {
  const { userToken, adminToken, logoutUser, logoutAdmin } = useAuth();
  const [health, setHealth] = useState<"ok" | "down" | "unknown">("unknown");
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    if (typeof window === "undefined") return "light";
    const saved = window.localStorage.getItem("jobboard_theme");
    return saved === "dark" ? "dark" : "light";
  });

  useEffect(() => {
    let cancelled = false;
    async function ping() {
      try {
        await apiRequest(`/health/check`, {
          method: "GET",
          headers: {},
        });
        if (!cancelled) setHealth("ok");
      } catch {
        if (!cancelled) setHealth("down");
      }
    }
    ping();
    const id = window.setInterval(ping, 45000);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    window.localStorage.setItem("jobboard_theme", theme);
  }, [theme]);

  return (
    <>
      <header className="header">
        <div className="header-inner">
          <Link to="/" className="logo">
            Open<span className="logo-accent">Hire</span>
          </Link>
          <nav className="nav-links">
            <NavLink to="/" end>
              Jobs
            </NavLink>
            {userToken && (
              <>
                <NavLink to="/dashboard">Dashboard</NavLink>
                <NavLink to="/onboarding/profile">Profile</NavLink>
                <NavLink to="/onboarding/education">Education</NavLink>
              </>
            )}
            <NavLink to="/admin/login">Employers</NavLink>
            <button
              type="button"
              className="btn btn-ghost theme-toggle"
              onClick={() => setTheme((prev) => (prev === "light" ? "dark" : "light"))}
              aria-label="Toggle color theme"
            >
              {theme === "light" ? "Dark mode" : "Light mode"}
            </button>
            <span className="badge-online" title={`API ${getApiBase()}`}>
              <span className="badge-online-dot" />
              API {health === "ok" ? "live" : health === "down" ? "down" : "…"}
            </span>
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
              <>
                <NavLink to="/admin/jobs">Admin</NavLink>
                <button type="button" className="btn btn-ghost" onClick={logoutAdmin}>
                  Leave admin
                </button>
              </>
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
              Premium recruiting site. Built for fast applications, clear
              pipelines, and clean operations.
            </p>
          </div>
          <div className="footer-col">
            <h4>Platform</h4>
            <Link to="/">Jobs</Link>
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/admin/jobs">Admin console</Link>
          </div>
          <div className="footer-col">
            <h4>Account</h4>
            <Link to="/register">Register</Link>
            <Link to="/login">Sign in</Link>
            <Link to="/verify">Verify account</Link>
          </div>
          <div className="footer-col">
            <h4>Deploy</h4>
            <p>
              Connect to OpenHire to get amazing job offers around the world,
              We are here to connect you to the rest of the world.
            </p>
          </div>
        </div>
        <div className="footer-bottom">
          <span>OpenHire · Designed for high-trust hiring journeys</span>
          <span>API status: {health === "ok" ? "Live" : health === "down" ? "Offline" : "Checking"}</span>
        </div>
      </footer>
    </>
  );
}
