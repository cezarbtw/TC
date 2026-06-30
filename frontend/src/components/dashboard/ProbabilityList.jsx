import { useEffect, useMemo, useRef } from 'react';
import { EMOTIONS } from '../../utils/constants';

export function ProbabilityList({ probabilities }) {
  const containerRef = useRef(null);

  const sorted = useMemo(
    () =>
      Object.entries(probabilities || {}).sort((a, b) => b[1] - a[1]),
    [probabilities]
  );

  useEffect(() => {
    if (!containerRef.current) return;
    const fills = containerRef.current.querySelectorAll('.probability-fill');
    fills.forEach((el) => (el.style.width = '0'));
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        sorted.forEach(([, val], i) => {
          if (fills[i]) fills[i].style.width = `${val}%`;
        });
      });
    });
  }, [sorted]);

  return (
    <div className="probabilities-list" ref={containerRef}>
      {sorted.map(([key, val]) => {
        const emo = EMOTIONS[key];
        return (
          <div key={key} className="probability-item">
            <div className="probability-meta">
              <span className="probability-label">{emo.label}</span>
              <span className="probability-value">{val}%</span>
            </div>
            <div
              className="probability-bar"
              role="progressbar"
              aria-valuenow={val}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label={`Probabilidade de ${emo.label}`}
            >
              <div
                className="probability-fill"
                style={{ background: emo.color }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
