export function Button({
  children,
  variant = 'primary',
  type = 'button',
  className = '',
  ...rest
}) {
  const variantClass = variant === 'primary' ? 'btn-primary' : 'btn-ghost';
  return (
    <button
      type={type}
      className={`btn ${variantClass} ${className}`.trim()}
      {...rest}
    >
      {children}
    </button>
  );
}
