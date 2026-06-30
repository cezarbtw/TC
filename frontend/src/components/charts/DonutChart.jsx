import { useMemo } from 'react';
import { Doughnut } from 'react-chartjs-2';
import { EMOTIONS } from '../../utils/constants';
import { baseTooltipStyle } from './chartSetup';

export function DonutChart({ probabilities }) {
  const { data, options, keys } = useMemo(() => {
    const keys = Object.keys(probabilities || {});
    const values = keys.map((k) => probabilities[k]);
    const colors = keys.map((k) => EMOTIONS[k].color);
    return {
      keys,
      data: {
        labels: keys.map((k) => EMOTIONS[k].label),
        datasets: [
          {
            data: values,
            backgroundColor: colors,
            borderColor: '#1c1e2e',
            borderWidth: 3,
            hoverOffset: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        cutout: '68%',
        plugins: {
          legend: { display: false },
          tooltip: {
            ...baseTooltipStyle,
            callbacks: {
              label: (ctx) => `${ctx.label}: ${ctx.parsed}%`,
            },
          },
        },
      },
    };
  }, [probabilities]);

  return (
    <div className="donut-container">
      <div className="donut-wrapper">
        <Doughnut data={data} options={options} />
      </div>
      <div className="donut-legend">
        {keys.map((k) => (
          <div key={k} className="legend-item">
            <span
              className="legend-dot"
              style={{ background: EMOTIONS[k].color }}
            />
            <span className="legend-label">{EMOTIONS[k].label}</span>
            <span className="legend-value">{probabilities[k]}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
