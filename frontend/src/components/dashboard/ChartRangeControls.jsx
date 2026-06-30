const RANGES = [
  { value: 'all', label: 'Completo' },
  { value: '30', label: '30s' },
  { value: '60', label: '60s' },
];

export function ChartRangeControls({ range, onChange }) {
  return (
    <div className="chart-controls" role="group" aria-label="Intervalo do gráfico">
      {RANGES.map((r) => (
        <button
          key={r.value}
          type="button"
          className={`chart-btn${range === r.value ? ' active' : ''}`}
          onClick={() => onChange(r.value)}
          aria-pressed={range === r.value}
        >
          {r.label}
        </button>
      ))}
    </div>
  );
}
