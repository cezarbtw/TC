import { EMOTIONS } from '../../utils/constants';

export function EmotionTag({ emotion }) {
  const emo = EMOTIONS[emotion];
  if (!emo) return null;
  return (
    <span
      className="emotion-tag"
      style={{ background: `${emo.color}18`, color: emo.color }}
    >
      {emo.label}
    </span>
  );
}
