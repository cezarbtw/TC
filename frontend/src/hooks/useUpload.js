import { useCallback, useState } from 'react';
import { sessionsService } from '../services/sessionsService';
import {
  ACCEPTED_VIDEO_EXT,
  ACCEPTED_VIDEO_TYPES,
  MAX_UPLOAD_BYTES,
} from '../utils/constants';

export function useUpload() {
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('idle');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const validate = useCallback((f) => {
    if (!f) return 'Arquivo inválido.';
    const ext = '.' + (f.name.split('.').pop() || '').toLowerCase();
    const validType =
      ACCEPTED_VIDEO_TYPES.includes(f.type) ||
      ACCEPTED_VIDEO_EXT.includes(ext);
    if (!validType) {
      return 'Formato não suportado. Use MP4, AVI ou MOV.';
    }
    if (f.size > MAX_UPLOAD_BYTES) {
      return 'O arquivo excede o limite de 200 MB.';
    }
    return null;
  }, []);

  const start = useCallback(
    async (f) => {
      const err = validate(f);
      if (err) {
        setError(err);
        setStatus('error');
        return { ok: false, error: err };
      }
      setFile(f);
      setProgress(0);
      setError(null);
      setStatus('uploading');
      try {
        const session = await sessionsService.upload(f, setProgress);
        setResult(session);
        setStatus('success');
        return { ok: true, session };
      } catch (e) {
        const msg = e.friendlyMessage || 'Falha ao processar o vídeo.';
        setError(msg);
        setStatus('error');
        return { ok: false, error: msg };
      }
    },
    [validate]
  );

  const reset = useCallback(() => {
    setFile(null);
    setProgress(0);
    setStatus('idle');
    setResult(null);
    setError(null);
  }, []);

  return { file, progress, status, result, error, start, reset, validate };
}
