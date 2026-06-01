import { useDeferredValue, useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { apiRequest, ApiError } from "../api/client";
import { employmentLabel, jobStatusLabel } from "../lib/labels";

type JobRow = {
  job_id: number;
  title: string;
  company_name?: string;
  location?: string;
  employment_type?: string | number;
  status?: string | number;
};

type JobsResponse = {
  result: {
    page: number;
    limit: number;
    count: number;
    jobs: JobRow[];
  };
};

function statusPillClass(code: string | number | undefined | null): string {
  const label = jobStatusLabel(code).toLowerCase();
  if (label === "open")   return "pill status-open";
  if (label === "closed") return "pill status-closed";
  if (label === "draft")  return "pill status-draft";
  return "pill pill-subtle";
}

export default function HomePage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [page, setPage] = useState(() => {
    const p = Number(searchParams.get("page") ?? "1");
    return Number.isFinite(p) && p > 0 ? p : 1;
  });
  const [query, setQuery] = useState(() => searchParams.get("q") ?? "");
  const [location, setLocation] = useState(() => searchParams.get("loc") ?? "");
  const [selectedCategory, setSelectedCategory] = useState(() => searchParams.get("cat") ?? "All");
  const [selectedStatus, setSelectedStatus] = useState(() => searchParams.get("status") ?? "All");
  const [data, setData] = useState<JobsResponse["result"] | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [showFilters, setShowFilters] = useState(false);
  const pageSize = 12;

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setErr(null);
    apiRequest<JobsResponse>(`/public/jobs?page=1&limit=100`, { method: "GET" })
      .then((res) => { if (!cancelled) setData(res.result); })
      .catch((e) => { if (!cancelled) setErr(e instanceof ApiError ? e.message : "Could not load jobs"); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  const allJobs = useMemo(() => data?.jobs ?? [], [data]);
  const deferredQuery    = useDeferredValue(query);
  const deferredLocation = useDeferredValue(location);
  const normalizedQuery    = deferredQuery.trim().toLowerCase();
  const normalizedLocation = deferredLocation.trim().toLowerCase();

  const categoryOptions = useMemo(
    () => ["All", ...new Set(allJobs.map((j) => employmentLabel(j.employment_type)))],
    [allJobs]
  );
  const statusOptions = useMemo(
    () => ["All", ...new Set(allJobs.map((j) => jobStatusLabel(j.status)))],
    [allJobs]
  );

  const filteredJobs = useMemo(
    () =>
      allJobs.filter((j) => {
        const matchesQuery =
          normalizedQuery.length === 0 ||
          `${j.title} ${j.company_name ?? ""}`.toLowerCase().includes(normalizedQuery);
        const matchesLocation =
          normalizedLocation.length === 0 ||
          `${j.location ?? ""}`.toLowerCase().includes(normalizedLocation);
        const matchesCategory =
          selectedCategory === "All" || employmentLabel(j.employment_type) === selectedCategory;
        const matchesStatus =
          selectedStatus === "All" || jobStatusLabel(j.status) === selectedStatus;
        return matchesQuery && matchesLocation && matchesCategory && matchesStatus;
      }),
    [allJobs, normalizedLocation, normalizedQuery, selectedCategory, selectedStatus]
  );

  const pageCount = Math.max(1, Math.ceil(filteredJobs.length / pageSize));
  const safePage  = Math.min(page, pageCount);
  const pagedJobs = useMemo(() => {
    const start = (safePage - 1) * pageSize;
    return filteredJobs.slice(start, start + pageSize);
  }, [filteredJobs, safePage]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (page > 1) params.set("page", String(page));
    if (query.trim()) params.set("q", query.trim());
    if (location.trim()) params.set("loc", location.trim());
    if (selectedCategory !== "All") params.set("cat", selectedCategory);
    if (selectedStatus !== "All") params.set("status", selectedStatus);
    setSearchParams(params, { replace: true });
  }, [location, page, query, selectedCategory, selectedStatus, setSearchParams]);

  function companyInitial(name: string) {
    const t = name.trim();
    return t ? t.charAt(0).toUpperCase() : "?";
  }

  const hasFilters = query.trim() || location.trim() || selectedCategory !== "All" || selectedStatus !== "All";

  return (
    <>
      {/* ── HERO ── */}
      <section className="home-hero" aria-label="Hero">
        <div className="home-hero-bg" aria-hidden />
        <div className="home-hero-inner">
          <div className="headline-row home-hero-row">
            <div className="hero-main">
              <p className="home-eyebrow">Open roles · updated live</p>
              <h1 className="display home-hero-title">Roles worth your next chapter</h1>
              <p className="tagline home-hero-tagline">
                Discover opportunities from employers you can trust — search, filter, and apply
                in one streamlined experience.
              </p>

              {/* Inline search bar in hero */}
              <div className="home-search-bar">
                <div className="search-input-wrap">
                  <svg className="search-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M9 3a6 6 0 100 12A6 6 0 009 3zm-8 6a8 8 0 1114.32 4.906l4.387 4.387a1 1 0 01-1.414 1.414l-4.387-4.387A8 8 0 011 9z" clipRule="evenodd" />
                  </svg>
                  <input
                    value={query}
                    onChange={(e) => { setPage(1); setQuery(e.target.value); }}
                    placeholder="Role or company…"
                    aria-label="Search by role or company"
                  />
                </div>
                <div className="search-input-wrap">
                  <svg className="search-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                  </svg>
                  <input
                    value={location}
                    onChange={(e) => { setPage(1); setLocation(e.target.value); }}
                    placeholder="City or Remote…"
                    aria-label="Search by location"
                  />
                </div>
              </div>

              <div className="stack home-hero-pills" style={{ marginTop: "1rem" }}>
                <span className="pill pill-accent">Verified pipeline</span>
                <span className="pill">Smart filters</span>
                <span className="pill">Guided apply</span>
              </div>
            </div>

            <div className="detail-shell hero-stat home-hero-stat">
              <p className="hero-stat-label">Matching roles</p>
              <p className="hero-stat-value">{loading ? "—" : filteredJobs.length}</p>
              <p className="hero-stat-label">live on the board right now</p>
              <div className="stack" style={{ marginTop: "1rem" }}>
                <Link to="/register" className="btn btn-primary" style={{ flex: 1, justifyContent: "center" }}>
                  Get started free
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {err && (
        <div className="alert alert-error" style={{ marginBottom: "1.25rem" }}>
          {err}
        </div>
      )}

      {/* ── LOADING SKELETONS ── */}
      {loading && (
        <div className="card-grid jobs-results">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="job-card job-card-skeleton">
              <div className="job-card-top">
                <div className="skeleton-logo" />
                <div style={{ flex: 1 }}>
                  <div className="skeleton-line" style={{ width: "45%" }} />
                  <div className="skeleton-line" style={{ width: "85%", marginTop: 10 }} />
                </div>
              </div>
              <div className="skeleton-line" style={{ width: "100%", marginTop: 14 }} />
              <div className="skeleton-line" style={{ width: "60%", marginTop: 8 }} />
            </div>
          ))}
        </div>
      )}

      {/* ── JOB FEED ── */}
      {!loading && data && (
        <>
          <div className="jobs-stage home-feed-wrap">
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "0.75rem", marginBottom: "1.25rem" }}>
              <div className="home-feed-head" style={{ margin: 0 }}>
                <h2 className="home-feed-title">Open positions</h2>
                <p className="home-feed-sub">
                  {filteredJobs.length} role{filteredJobs.length === 1 ? "" : "s"} available
                  {hasFilters ? " · refined by your filters" : ""}
                </p>
              </div>
              <div className="mobile-filter-actions" style={{ display: "flex" }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowFilters((s) => !s)}
                >
                  {showFilters ? "Hide filters" : "⊞ Filters"}
                </button>
                {hasFilters && (
                  <button
                    type="button"
                    className="btn btn-ghost"
                    onClick={() => { setPage(1); setQuery(""); setLocation(""); setSelectedCategory("All"); setSelectedStatus("All"); }}
                  >
                    Reset
                  </button>
                )}
              </div>
            </div>

            <div className="jobs-layout">
              {/* Filters sidebar */}
              <aside className={`filters-panel ${showFilters ? "show-mobile" : ""}`}>
                <p className="filters-title">Refine results</p>

                <div className="field" style={{ marginBottom: "0.85rem" }}>
                  <label>Category</label>
                  <select value={selectedCategory} onChange={(e) => { setPage(1); setSelectedCategory(e.target.value); }}>
                    {categoryOptions.map((opt) => <option key={opt} value={opt}>{opt}</option>)}
                  </select>
                </div>

                <div className="field" style={{ marginBottom: "0.85rem" }}>
                  <label>Status</label>
                  <select value={selectedStatus} onChange={(e) => { setPage(1); setSelectedStatus(e.target.value); }}>
                    {statusOptions.map((opt) => <option key={opt} value={opt}>{opt}</option>)}
                  </select>
                </div>

                {hasFilters && (
                  <button
                    type="button"
                    className="btn btn-ghost"
                    style={{ width: "100%", justifyContent: "center", marginTop: "0.25rem" }}
                    onClick={() => { setPage(1); setQuery(""); setLocation(""); setSelectedCategory("All"); setSelectedStatus("All"); }}
                  >
                    Reset all filters
                  </button>
                )}

                {/* Active filter chips */}
                {hasFilters && (
                  <div className="stack" style={{ marginTop: "0.85rem", flexWrap: "wrap" }}>
                    {query && <span className="pill pill-accent">"{query}"</span>}
                    {location && <span className="pill pill-accent">📍 {location}</span>}
                    {selectedCategory !== "All" && <span className="pill pill-accent">{selectedCategory}</span>}
                    {selectedStatus !== "All" && <span className="pill pill-accent">{selectedStatus}</span>}
                  </div>
                )}
              </aside>

              {/* Job cards grid */}
              <div className="card-grid jobs-results">
                {pagedJobs.length === 0 && (
                  <div className="home-empty">
                    <p style={{ margin: "0 0 0.5rem", fontWeight: 600 }}>No roles match your filters</p>
                    <p style={{ margin: 0, fontSize: "0.9rem" }}>Try broadening your search or resetting filters.</p>
                  </div>
                )}
                {pagedJobs.map((j) => {
                  const company = j.company_name || "Company";
                  return (
                    <Link key={j.job_id} to={`/jobs/${j.job_id}`} className="job-card-link">
                      <article className="job-card-premium">
                        <div className="job-card-top">
                          <div className="job-card-logo" aria-hidden>
                            {companyInitial(company)}
                          </div>
                          <div className="job-card-headline">
                            <p className="job-card-company">{company}</p>
                            <h3 className="job-card-title">{j.title}</h3>
                          </div>
                        </div>
                        <div className="job-card-meta-row">
                          <span>{j.location || "Remote / TBD"}</span>
                          <span className="job-card-meta-dot" aria-hidden />
                          <span>{employmentLabel(j.employment_type)}</span>
                        </div>
                        <div className="job-card-footer">
                          <span className={statusPillClass(j.status)}>
                            {jobStatusLabel(j.status)}
                          </span>
                          <span className="job-card-cta">
                            View role
                            <span className="job-card-cta-arrow" aria-hidden> →</span>
                          </span>
                        </div>
                      </article>
                    </Link>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Pagination */}
          {pageCount > 1 && (
            <nav className="pagination-bar" aria-label="Job list pages">
              <button
                type="button"
                className="btn btn-secondary pagination-btn"
                disabled={safePage <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                ← Previous
              </button>
              <span className="pagination-meta">
                Page <strong>{safePage}</strong> of <strong>{pageCount}</strong>
                <span style={{ marginLeft: "0.5rem", color: "var(--text-faint)" }}>
                  ({filteredJobs.length} total)
                </span>
              </span>
              <button
                type="button"
                className="btn btn-secondary pagination-btn"
                disabled={safePage >= pageCount}
                onClick={() => setPage((p) => p + 1)}
              >
                Next →
              </button>
            </nav>
          )}
        </>
      )}
    </>
  );
}
