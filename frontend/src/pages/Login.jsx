import { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function Login() {
  const { user, login, sessionExpired } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (user) {
    return <Navigate to="/" replace />;
  }

  async function submit(event) {
    event.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await login(username, password);
    } catch (requestError) {
      setError(requestError.friendlyMessage || 'Não foi possível entrar.');
      setSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <form className="login-card" onSubmit={submit}>
        <p className="login-eyebrow">EMOTIONLENS</p>
        <h1>Acesse sua área profissional</h1>
        <p className="login-description">Use as credenciais fornecidas pelo administrador.</p>
        <label htmlFor="username">Usuário</label>
        <input
          id="username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          autoComplete="username"
          required
        />
        <label htmlFor="password">Senha</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="current-password"
          required
        />
        {error && <p className="login-error" role="alert">{error}</p>}
        <button type="submit" className="login-submit" disabled={submitting}>
          {submitting ? 'Entrando...' : 'Entrar'}
        </button>
        {sessionExpired && <p className="login-expired">Sua sessão expirou. Entre novamente.</p>}
      </form>
    </main>
  );
}
