import { NavLink } from 'react-router-dom';
import {
  IconDashboard,
  IconLogo,
  IconSessions,
  IconUpload,
} from '../ui/Icon';

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', Icon: IconDashboard, end: true },
  { to: '/sessions', label: 'Sessões', Icon: IconSessions },
  { to: '/upload', label: 'Upload', Icon: IconUpload },
];

export function Sidebar({ open, onClose }) {
  return (
    <>
      {open && (
        <div
          className="sidebar-backdrop show"
          onClick={onClose}
          aria-hidden="true"
        />
      )}
      <aside className={`sidebar${open ? ' open' : ''}`} id="sidebar">
        <div className="sidebar-header">
          <div className="logo">
            <div className="logo-icon">
              <IconLogo />
            </div>
            <span className="logo-text">EmotionLens</span>
          </div>
          <span className="badge-academic">Protótipo Acadêmico</span>
        </div>

        <nav className="sidebar-nav" aria-label="Navegação principal">
          {NAV_ITEMS.map(({ to, label, Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={onClose}
              className={({ isActive }) =>
                `nav-item${isActive ? ' active' : ''}`
              }
            >
              <Icon />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <p className="footer-text">TCC — Ciência da Computação</p>
          <p className="footer-text muted">Versão 1.0 • 2026</p>
        </div>
      </aside>
    </>
  );
}
