export function StatCard({
  label,
  value,
  sub,
  icon,
  highlight = false,
  iconClassName = '',
}) {
  return (
    <div className={`stat-card${highlight ? ' highlight' : ''}`}>
      <div className={`stat-icon ${iconClassName}`.trim()}>{icon}</div>
      <div className="stat-info">
        <span className="stat-label">{label}</span>
        <span className="stat-value">{value}</span>
        {sub && <span className="stat-sub">{sub}</span>}
      </div>
    </div>
  );
}
