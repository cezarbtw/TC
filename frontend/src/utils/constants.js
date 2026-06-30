export const EMOTIONS = {
  feliz: { color: '#fbbf24', label: 'Feliz' },
  triste: { color: '#60a5fa', label: 'Triste' },
  raiva: { color: '#f87171', label: 'Raiva' },
  surpresa: { color: '#fb923c', label: 'Surpresa' },
  medo: { color: '#a78bfa', label: 'Medo' },
  nojo: { color: '#34d399', label: 'Nojo' },
  neutro: { color: '#94a3b8', label: 'Neutro' },
};

export const EMOTION_KEYS = Object.keys(EMOTIONS);

export const MAX_UPLOAD_BYTES = 200 * 1024 * 1024;

export const ACCEPTED_VIDEO_TYPES = [
  'video/mp4',
  'video/avi',
  'video/x-msvideo',
  'video/quicktime',
];

export const ACCEPTED_VIDEO_EXT = ['.mp4', '.avi', '.mov'];
