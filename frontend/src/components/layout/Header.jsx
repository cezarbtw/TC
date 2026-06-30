import { IconMenu } from '../ui/Icon';

export function Header({ title, onMenuClick }) {
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
          <div className="avatar" aria-hidden="true">P</div>
          <span className="user-name">Psicólogo(a)</span>
        </div>
      </div>
    </header>
  );
}
