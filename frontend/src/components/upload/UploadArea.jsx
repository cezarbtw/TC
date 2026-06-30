import { useRef, useState } from 'react';
import { IconUploadLarge } from '../ui/Icon';

export function UploadArea({ onSelect }) {
  const inputRef = useRef(null);
  const [dragover, setDragover] = useState(false);

  const trigger = () => inputRef.current?.click();

  return (
    <div
      className={`upload-area${dragover ? ' dragover' : ''}`}
      onClick={trigger}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          trigger();
        }
      }}
      onDragOver={(e) => {
        e.preventDefault();
        setDragover(true);
      }}
      onDragLeave={() => setDragover(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragover(false);
        if (e.dataTransfer.files.length) {
          onSelect(e.dataTransfer.files[0]);
        }
      }}
      role="button"
      tabIndex={0}
      aria-label="Selecionar vídeo para upload"
    >
      <div className="upload-icon">
        <IconUploadLarge />
      </div>
      <h3 className="upload-title">Arraste um vídeo aqui</h3>
      <p className="upload-subtitle">ou clique para selecionar um arquivo</p>
      <p className="upload-formats">
        Formatos aceitos: MP4, AVI, MOV • Máx. 200 MB
      </p>
      <input
        ref={inputRef}
        type="file"
        accept="video/mp4,video/avi,video/quicktime,.mp4,.avi,.mov"
        hidden
        onChange={(e) => {
          if (e.target.files?.length) onSelect(e.target.files[0]);
          e.target.value = '';
        }}
      />
    </div>
  );
}
