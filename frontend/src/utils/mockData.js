import { EMOTION_KEYS } from './constants';

export function generateTimeline(frames) {
  const points = Math.min(frames, 30);
  const data = {};
  EMOTION_KEYS.forEach((k) => (data[k] = []));
  for (let i = 0; i < points; i++) {
    let remaining = 100;
    EMOTION_KEYS.forEach((k, idx) => {
      if (idx === EMOTION_KEYS.length - 1) {
        data[k].push(Math.max(0, remaining));
      } else {
        const val = Math.floor(
          Math.random() * (remaining / (EMOTION_KEYS.length - idx))
        );
        data[k].push(val);
        remaining -= val;
      }
    });
  }
  return data;
}

export const mockSessions = [
  {
    id: 1,
    name: 'Sessão 01',
    date: '2026-03-28',
    duration: '02:34',
    frames: 154,
    predominant: 'feliz',
    confidence: 72,
    probabilities: { feliz: 72, triste: 8, raiva: 3, surpresa: 5, medo: 2, nojo: 1, neutro: 9 },
    timeline: generateTimeline(154),
  },
  {
    id: 2,
    name: 'Sessão 02',
    date: '2026-03-30',
    duration: '03:12',
    frames: 192,
    predominant: 'neutro',
    confidence: 58,
    probabilities: { feliz: 15, triste: 12, raiva: 5, surpresa: 3, medo: 4, nojo: 3, neutro: 58 },
    timeline: generateTimeline(192),
  },
  {
    id: 3,
    name: 'Sessão 03',
    date: '2026-04-01',
    duration: '01:45',
    frames: 105,
    predominant: 'triste',
    confidence: 65,
    probabilities: { feliz: 10, triste: 65, raiva: 5, surpresa: 2, medo: 8, nojo: 1, neutro: 9 },
    timeline: generateTimeline(105),
  },
  {
    id: 4,
    name: 'Sessão 04',
    date: '2026-04-03',
    duration: '04:10',
    frames: 250,
    predominant: 'surpresa',
    confidence: 48,
    probabilities: { feliz: 20, triste: 5, raiva: 8, surpresa: 48, medo: 7, nojo: 2, neutro: 10 },
    timeline: generateTimeline(250),
  },
  {
    id: 5,
    name: 'Sessão 05',
    date: '2026-04-06',
    duration: '02:58',
    frames: 178,
    predominant: 'feliz',
    confidence: 61,
    probabilities: { feliz: 61, triste: 7, raiva: 4, surpresa: 10, medo: 3, nojo: 2, neutro: 13 },
    timeline: generateTimeline(178),
  },
];

export function createMockSession(filename, nextId) {
  const id = nextId;
  const predominant =
    EMOTION_KEYS[Math.floor(Math.random() * EMOTION_KEYS.length)];
  const confidence = Math.floor(Math.random() * 35 + 40);
  const probs = {};
  let remaining = 100 - confidence;
  probs[predominant] = confidence;
  const rest = EMOTION_KEYS.filter((k) => k !== predominant);
  rest.forEach((k, i) => {
    if (i === rest.length - 1) {
      probs[k] = Math.max(0, remaining);
    } else {
      const v = Math.floor(Math.random() * (remaining / (rest.length - i)));
      probs[k] = v;
      remaining -= v;
    }
  });
  const frames = Math.floor(Math.random() * 200 + 60);
  return {
    id,
    name: `Sessão ${String(id).padStart(2, '0')}`,
    sourceFile: filename,
    date: new Date().toISOString().split('T')[0],
    duration: `0${Math.floor(Math.random() * 4 + 1)}:${String(
      Math.floor(Math.random() * 60)
    ).padStart(2, '0')}`,
    frames,
    predominant,
    confidence,
    probabilities: probs,
    timeline: generateTimeline(frames),
  };
}
