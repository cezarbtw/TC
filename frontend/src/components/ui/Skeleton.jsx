export function Skeleton({ width = '100%', height = 14, style, ...rest }) {
  return (
    <div
      className="skeleton"
      style={{ width, height, ...style }}
      aria-hidden="true"
      {...rest}
    />
  );
}
