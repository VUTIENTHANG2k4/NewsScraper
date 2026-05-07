import { Link, NavLink } from "react-router-dom";

const IconNews = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
    <path d="M4 4h12a2 2 0 012 2v1M4 8h12M4 12h8m-8 4h8" strokeLinecap="round" />
    <rect x="4" y="4" width="16" height="16" rx="2" />
  </svg>
);

const IconGrid = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
    <rect x="3" y="3" width="7" height="7" rx="1" />
    <rect x="14" y="3" width="7" height="7" rx="1" />
    <rect x="3" y="14" width="7" height="7" rx="1" />
    <rect x="14" y="14" width="7" height="7" rx="1" />
  </svg>
);

const IconPlus = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
    <path d="M12 5v14M5 12h14" strokeLinecap="round" />
  </svg>
);

const linkClass = ({ isActive }) => (isActive ? "active" : undefined);

export default function Navbar() {
  return (
    <nav className="top-nav" role="navigation" aria-label="Chính">
      <Link to="/" className="top-nav__brand">
        <span className="top-nav__brand-icon" aria-hidden>
          N
        </span>
        <span>News Scraper</span>
      </Link>
      <div className="top-nav__links">
        <NavLink to="/" end className={linkClass}>
          <IconNews />
          Tin tức
        </NavLink>
        <NavLink to="/dashboard" className={linkClass}>
          <IconGrid />
          Quản lý nguồn
        </NavLink>
        <NavLink to="/them-nguon" className={linkClass}>
          <IconPlus />
          Thêm nguồn
        </NavLink>
      </div>
    </nav>
  );
}
