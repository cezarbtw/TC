import { IconMenu } from '../ui/Icon';
import { useAuth } from '../../hooks/useAuth';

export function Header({ title, onMenuClick }) {
  const { user, logout } = useAuth();
  const initial = user?.display_name?.trim().charAt(0).toUpperCase() || 'U';
  return (
    <header className="top-header">
      <div className="header-left">
        <button
          type="button"
          className="menu-toggle"
          onClick={onMenuClick}
          aria-label="Abrir menu"
        >
          <IconMenu />
        </button>
        <h1 className="page-title">{title}</h1>
      </div>
      <div className="header-right">
        <div className="user-info">
          <div className="avatar" aria-hidden="true">{initial}</div>
          <span className="user-name">{user?.display_name}</span>
          <button type="button" className="logout-button" onClick={logout}>Sair</button>
        </div>
      </div>
    </header>
  );
}
