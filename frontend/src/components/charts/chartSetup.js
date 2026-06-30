import {
  ArcElement,
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  LineElement,
  PointElement,
  ArcElement,
  Filler,
  Legend,
  Tooltip
);

export const baseTooltipStyle = {
  backgroundColor: '#1c1e2e',
  borderColor: 'rgba(255,255,255,0.1)',
  borderWidth: 1,
  titleColor: '#e8eaf0',
  bodyColor: '#8b8fa7',
  titleFont: { family: 'Inter', weight: '600' },
  bodyFont: { family: 'Inter' },
  padding: 12,
  cornerRadius: 8,
};
