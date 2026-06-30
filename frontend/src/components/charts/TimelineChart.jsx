import { useMemo } from 'react';
import { Line } from 'react-chartjs-2';
import { EMOTIONS, EMOTION_KEYS } from '../../utils/constants';
import { baseTooltipStyle } from './chartSetup';

export function TimelineChart({ timeline, range = 'all' }) {
  const sliced = useMemo(() => {
    if (!timeline) return null;
    if (range === 'all') return timeline;
    const limit = parseInt(range, 10);
    const out = {};
    EMOTION_KEYS.forEach((k) => {
      out[k] = (timeline[k] || []).slice(0, limit);
    });
    return out;
  }, [timeline, range]);

  const data = useMemo(() => {
    if (!sliced) return { labels: [], datasets: [] };
    const labels = (sliced[EMOTION_KEYS[0]] || []).map((_, i) => `${i + 1}s`);
    const datasets = EMOTION_KEYS.map((k) => ({
      label: EMOTIONS[k].label,
      data: sliced[k] || [],
      borderColor: EMOTIONS[k].color,
      backgroundColor: EMOTIONS[k].color + '18',
      borderWidth: 2,
      pointRadius: 0,
      pointHoverRadius: 4,
      tension: 0.4,
      fill: false,
    }));
    return { labels, datasets };
  }, [sliced]);

  const options = useMemo(
    () => ({
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: '#8b8fa7',
            font: { family: 'Inter', size: 11 },
            boxWidth: 12,
            boxHeight: 3,
            padding: 16,
            usePointStyle: false,
          },
        },
        tooltip: {
          ...baseTooltipStyle,
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y}%`,
          },
        },
      },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.03)' },
          ticks: {
            color: '#5a5e78',
            font: { family: 'Inter', size: 10 },
            maxTicksLimit: 10,
          },
        },
        y: {
          min: 0,
          max: 100,
          grid: { color: 'rgba(255,255,255,0.03)' },
          ticks: {
            color: '#5a5e78',
            font: { family: 'Inter', size: 10 },
            callback: (v) => `${v}%`,
          },
        },
      },
    }),
    []
  );

  return (
    <div role="img" aria-label="Gráfico de emoções ao longo do tempo">
      <Line data={data} options={options} />
    </div>
  );
}
