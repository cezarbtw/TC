import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { SessionsTable } from '../components/sessions/SessionsTable';
import { IconUploadSmall } from '../components/ui/Icon';
import { useSessions } from '../context/SessionsContext';

export function Sessions() {
  const navigate = useNavigate();
  const { sessions, selectSession, loading } = useSessions();
  const [query, setQuery] = useState('');

  const filtered = useMemo(() => {
    if (!query.trim()) return sessions;
    const q = query.toLowerCase();
    return sessions.filter(
      (s) =>
        s.name.toLowerCase().includes(q) ||
        s.predominant.toLowerCase().includes(q) ||
        s.date.includes(q)
    );
  }, [sessions, query]);

  const handleSelect = (session) => {
    selectSession(session);
    navigate('/');
  };

  return (
    <>
      <div className="section-header">
        <h2 className="section-title">Sessões Analisadas</h2>
        <div className="section-actions">
          <input
            type="search"
            className="search-input"
            placeholder="Buscar por nome, emoção ou data..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            aria-label="Buscar sessões"
          />
          <Button onClick={() => navigate('/upload')}>
            <IconUploadSmall />
            Novo Upload
          </Button>
        </div>
      </div>
      <div className="sessions-table-wrapper">
        <SessionsTable
          sessions={filtered}
          onSelect={handleSelect}
          loading={loading}
        />
      </div>
    </>
  );
}
