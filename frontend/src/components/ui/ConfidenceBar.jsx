export function ConfidenceBar({ value }) {
  const v = Math.max(0, Math.min(100, value || 0));
  return (
    <div className="confidence-bar-mini">
      <div className="bar" aria-hidden="true">
        <div className="fill" style={{ width: `${v}%` }} />
      </div>
      <span>{v}%</span>
    </div>
  );
}
