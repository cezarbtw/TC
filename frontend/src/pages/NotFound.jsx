import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';

export function NotFound() {
  const navigate = useNavigate();
  return (
    <div className="not-found">
      <div className="not-found-code">404</div>
      <p className="not-found-text">Página não encontrada.</p>
      <Button onClick={() => navigate('/')}>Voltar ao Dashboard</Button>
    </div>
  );
}
