import { EMOTIONS } from '../../utils/constants';
import { formatDate } from '../../utils/formatters';

export function MiniSessions({ sessions, onSelect, limit = 4 }) {
  const list = sessions.slice(0, limit);
  return (
    <div className="sessions-mini-list">
      {list.map((s) => {
        const emo = EMOTIONS[s.predominant];
        return (
          <div
            key={s.id}
            className="session-mini-item"
            role="button"
            tabIndex={0}
            onClick={() => onSelect(s)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onSelect(s);
              }
            }}
            aria-label={`Selecionar ${s.name}`}
          >
            <div className="session-mini-info">
              <span className="session-mini-name">{s.name}</span>
              <span className="session-mini-date">{formatDate(s.date)}</span>
            </div>
            <span
              className="session-mini-emotion"
              style={{ color: emo.color }}
            >
              {emo.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}
