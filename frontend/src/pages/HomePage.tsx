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

export default function HomePage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [page, setPage] = useState(() => {
    const p = Number(searchParams.get("page") ?? "1");
    return Number.isFinite(p) && p > 0 ? p : 1;
  });
  const [query, setQuery] = useState(() => searchParams.get("q") ?? "");
  const [location, setLocation] = useState(() => searchParams.get("loc") ?? "");
  const [selectedCategory, setSelectedCategory] = useState(
    () => searchParams.get("cat") ?? "All"
  );
  const [selectedStatus, setSelectedStatus] = useState(
    () => searchParams.get("status") ?? "All"
  );
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
      .then((res) => {
        if (!cancelled) setData(res.result);
      })
      .catch((e) => {
        if (!cancelled)
          setErr(e instanceof ApiError ? e.message : "Could not load jobs");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const allJobs = useMemo(() => data?.jobs ?? [], [data]);
  const deferredQuery = useDeferredValue(query);
  const deferredLocation = useDeferredValue(location);
  const normalizedQuery = deferredQuery.trim().toLowerCase();
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
  const safePage = Math.min(page, pageCount);
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
    return t ? t.charAt(0).toUpperCase() : "—";
  }

  return (
    <>
      <section className="home-hero" aria-label="Featured intro">
        <div className="home-hero-bg" aria-hidden />
        <div className="home-hero-inner">
          <div className="headline-row home-hero-row">
            <div className="hero-main"  mt-12 >
              <p className="home-eyebrow">Open roles · updated live</p>
              <h1 className="display home-hero-title">Roles worth your next chapter</h1>
              <p className="tagline home-hero-tagline">
                Discover opportunities from employers you can trust search, filter, and apply in
                one streamlined experience.
              </p>
              <div className="stack home-hero-pills">
                <span className="pill pill-accent">Verified pipeline</span>
                <span className="pill">Smart filters</span>
                <span className="pill">Guided apply</span>
              </div>
            </div>
            <div className="detail-shell hero-stat home-hero-stat">
              <p className="hero-stat-label">Live board</p>
              <p className="hero-stat-value">{filteredJobs.length}</p>
              <p className="hero-stat-label">roles match your criteria</p>
            </div>
          </div>
        </div>
      </section>

      {err && (
        <p className="alert alert-error" style={{ marginBottom: "1rem" }}>
          {err}
        </p>
      )}

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
              <div className="skeleton-line" style={{ width: "60%", marginTop: 10 }} />
            </div>
          ))}
        </div>
      )}

      {!loading && data && (
        <>
          <div className="jobs-stage home-feed-wrap">
            <div className="home-feed-head">
              <h2 className="home-feed-title">Open positions</h2>
              <p className="home-feed-sub">
                {filteredJobs.length} role{filteredJobs.length === 1 ? "" : "s"} available
                {query.trim() || location.trim() ? " · refined by your filters" : ""}
              </p>
            </div>
            <div className="mobile-filter-actions">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowFilters((s) => !s)}
              >
                {showFilters ? "Hide filters" : "Show filters"}
              </button>
            </div>
            <div className="jobs-layout">
              <aside className={`detail-shell filters-panel ${showFilters ? "show-mobile" : ""}`}>
                <h3 className="filters-title">Refine results</h3>
                <div className="field">
                  <label>Keyword</label>
                  <input
                    value={query}
                    onChange={(e) => {
                      setPage(1);
                      setQuery(e.target.value);
                    }}
                    placeholder="Role or company"
                  />
                </div>
                <div className="field">
                  <label>Location</label>
                  <input
                    value={location}
                    onChange={(e) => {
                      setPage(1);
                      setLocation(e.target.value);
                    }}
                    placeholder="City or Remote"
                  />
                </div>
                <div className="field">
                  <label>Category</label>
                  <select
                    value={selectedCategory}
                    onChange={(e) => {
                      setPage(1);
                      setSelectedCategory(e.target.value);
                    }}
                  >
                    {categoryOptions.map((opt) => (
                      <option key={opt} value={opt}>
                        {opt}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="field">
                  <label>Status</label>
                  <select
                    value={selectedStatus}
                    onChange={(e) => {
                      setPage(1);
                      setSelectedStatus(e.target.value);
                    }}
                  >
                    {statusOptions.map((opt) => (
                      <option key={opt} value={opt}>
                        {opt}
                      </option>
                    ))}
                  </select>
                </div>
                <button
                  type="button"
                  className="btn btn-ghost"
                  onClick={() => {
                    setPage(1);
                    setQuery("");
                    setLocation("");
                    setSelectedCategory("All");
                    setSelectedStatus("All");
                  }}
                >
                  Reset filters
                </button>
              </aside>

              <div className="card-grid jobs-results">
                {pagedJobs.length === 0 && (
                  <p className="home-empty">No roles match your filters yet. Try broadening your search.</p>
                )}
                {pagedJobs.map((j) => {
                  const company = j.company_name || "Company";
                  return (
                    <Link key={j.job_id} to={`/jobs/${j.job_id}`} className="job-card-link">
                      <article className="job-card job-card-premium">
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
                          <span className="job-card-meta-item">{j.location || "Remote / TBD"}</span>
                          <span className="job-card-meta-dot" aria-hidden />
                          <span className="job-card-meta-item">{employmentLabel(j.employment_type)}</span>
                        </div>
                        <div className="job-card-footer">
                          <span className="pill pill-subtle">{jobStatusLabel(j.status)}</span>
                          <span className="job-card-cta">
                            View role
                            <span className="job-card-cta-arrow" aria-hidden>
                              →
                            </span>
                          </span>
                        </div>
                      </article>
                    </Link>
                  );
                })}
              </div>
            </div>
          </div>

          <nav className="pagination-bar section-spacer-top" aria-label="Job list pages">
            <button
              type="button"
              className="btn btn-secondary pagination-btn"
              disabled={safePage <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              Previous
            </button>
            <span className="pagination-meta">
              Page <strong>{safePage}</strong> of <strong>{pageCount}</strong>
            </span>
            <button
              type="button"
              className="btn btn-secondary pagination-btn"
              disabled={safePage >= pageCount}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </button>
          </nav>
        </>
      )}
    </>
  );
}
