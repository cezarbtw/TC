import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { sessionsService } from '../services/sessionsService';

const SessionsContext = createContext(null);

export function SessionsProvider({ children }) {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await sessionsService.list();
      setSessions(data);
      setCurrentSession((prev) => prev || data[0] || null);
    } catch (e) {
      setError(e.friendlyMessage || 'Erro ao carregar sessões.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const selectSession = useCallback((session) => {
    setCurrentSession(session);
  }, []);

  const addSession = useCallback((session) => {
    setSessions((prev) => [session, ...prev]);
    setCurrentSession(session);
  }, []);

  const value = {
    sessions,
    currentSession,
    loading,
    error,
    reload: load,
    selectSession,
    addSession,
  };

  return (
    <SessionsContext.Provider value={value}>
      {children}
    </SessionsContext.Provider>
  );
}

export function useSessions() {
  const ctx = useContext(SessionsContext);
  if (!ctx) {
    throw new Error('useSessions deve ser usado dentro de SessionsProvider');
  }
  return ctx;
}
