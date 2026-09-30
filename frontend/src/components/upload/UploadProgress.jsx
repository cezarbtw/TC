import { IconFile } from '../ui/Icon';

export function UploadProgress({ filename, progress }) {
  let label = 'Preparando arquivo...';
  if (progress >= 100) label = 'Laudo criptografado e salvo!';
  else if (progress > 90) label = 'Criptografando resultados (MCE + AES-256)...';
  else if (progress > 75) label = 'Aplicando suavização temporal nas emoções...';
  else if (progress > 50) label = 'HSEmotion: Classificando expressões faciais...';
  else if (progress > 25) label = 'YOLOv8: Extraindo frames e localizando rostos...';
  else if (progress > 0) label = 'Enviando pacote de vídeo seguro...';
  return (
    <div className="upload-progress">
      <div className="progress-file-info">
        <IconFile />
        <span className="progress-filename">{filename}</span>
      </div>
      <div
        className="progress-bar-track"
        role="progressbar"
        aria-valuenow={progress}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className="progress-bar-fill"
          style={{ width: `${Math.min(progress, 100)}%` }}
        />
      </div>
      <div className="progress-status">
        <span>{label}</span>
        <span>{Math.floor(Math.min(progress, 100))}%</span>
      </div>
    </div>
  );
}
