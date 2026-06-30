import { IconCheck } from '../ui/Icon';
import { Button } from '../ui/Button';

export function UploadSuccess({ onViewResults }) {
  return (
    <div className="upload-success">
      <div className="success-icon">
        <IconCheck />
      </div>
      <h3 className="success-title">Análise Concluída!</h3>
      <p className="success-subtitle">O vídeo foi processado com sucesso.</p>
      <Button onClick={onViewResults}>Ver Resultados</Button>
    </div>
  );
}
