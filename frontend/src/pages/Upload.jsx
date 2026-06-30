import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadArea } from '../components/upload/UploadArea';
import { UploadProgress } from '../components/upload/UploadProgress';
import { UploadSuccess } from '../components/upload/UploadSuccess';
import { useUpload } from '../hooks/useUpload';
import { useSessions } from '../context/SessionsContext';
import { useToast } from '../context/ToastContext';

export function Upload() {
  const navigate = useNavigate();
  const { addSession } = useSessions();
  const toast = useToast();
  const { file, progress, status, start, reset, error } = useUpload();

  useEffect(() => {
    if (status === 'error' && error) {
      toast.error('Falha no upload', error);
    }
  }, [status, error, toast]);

  const handleSelect = async (f) => {
    const result = await start(f);
    if (result.ok) {
      addSession(result.session);
      toast.success('Análise concluída', `${f.name} processado com sucesso.`);
    }
  };

  const handleViewResults = () => {
    reset();
    navigate('/');
  };

  return (
    <div className="upload-container">
      <div className="upload-card">
        {status === 'idle' || status === 'error' ? (
          <UploadArea onSelect={handleSelect} />
        ) : null}

        {status === 'uploading' && (
          <UploadProgress filename={file?.name} progress={progress} />
        )}

        {status === 'success' && (
          <UploadSuccess onViewResults={handleViewResults} />
        )}
      </div>

      <aside className="upload-info-card">
        <h3 className="info-title">Como funciona</h3>
        <ol className="info-steps">
          <li>Faça upload de um vídeo gravado durante uma sessão</li>
          <li>O sistema extrai frames e detecta expressões faciais</li>
          <li>As emoções são classificadas usando modelos de reconhecimento</li>
          <li>Os resultados são exibidos no dashboard</li>
        </ol>
        <div className="info-note">
          <strong>Nota:</strong> Este é um protótipo acadêmico. Os dados são
          simulados para fins de demonstração do TCC.
        </div>
      </aside>
    </div>
  );
}
