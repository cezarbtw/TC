import { IconFile } from '../ui/Icon';

export function UploadProgress({ filename, progress }) {
  const label = progress >= 100
    ? 'Análise concluída!'
    : progress > 50
      ? 'Analisando expressões...'
      : 'Enviando...';
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
