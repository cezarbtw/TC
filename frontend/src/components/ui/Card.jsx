export function Card({ children, className = '', ...rest }) {
  return (
    <div className={`card ${className}`.trim()} {...rest}>
      {children}
    </div>
  );
}

export function CardHeader({ title, badge, action, right }) {
  return (
    <div className="card-header">
      <h2 className="card-title">{title}</h2>
      {badge && <span className="card-badge">{badge}</span>}
      {action}
      {right}
    </div>
  );
}

export function CardBody({ children, className = '' }) {
  return <div className={`card-body ${className}`.trim()}>{children}</div>;
}
