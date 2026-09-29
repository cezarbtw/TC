import { createContext, useEffect, useState } from 'react';
import { api } from '../services/api';

export const AuthContext = createContext(null);

const TOKEN_KEY = 'emotionlens.access_token';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sessionExpired, setSessionExpired] = useState(false);

  useEffect(() => {
    async function restoreSession() {
      if (!localStorage.getItem(TOKEN_KEY)) {
        setLoading(false);
        return;
      }
      try {
        const { data } = await api.get('/auth/me');
        setUser(data);
      } catch {
        localStorage.removeItem(TOKEN_KEY);
      } finally {
        setLoading(false);
      }
    }

    function logoutOnUnauthorized() {
      setUser(null);
      setSessionExpired(true);
    }

    restoreSession();
    window.addEventListener('emotionlens:unauthorized', logoutOnUnauthorized);
    return () => window.removeEventListener('emotionlens:unauthorized', logoutOnUnauthorized);
  }, []);

  async function login(username, password) {
    const body = new URLSearchParams({ username, password });
    const { data } = await api.post('/auth/login', body, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    localStorage.setItem(TOKEN_KEY, data.access_token);
    const response = await api.get('/auth/me');
    setUser(response.data);
    setSessionExpired(false);
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    setUser(null);
    setSessionExpired(false);
  }

  return (
    <AuthContext.Provider value={{ user, loading, sessionExpired, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
