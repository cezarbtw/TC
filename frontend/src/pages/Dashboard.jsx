import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardBody, CardHeader } from '../components/ui/Card';
import { StatCard } from '../components/dashboard/StatCard';
import { ProbabilityList } from '../components/dashboard/ProbabilityList';
import { TimelineChart } from '../components/charts/TimelineChart';
import { DonutChart } from '../components/charts/DonutChart';
import { MiniSessions } from '../components/dashboard/MiniSessions';
import { ChartRangeControls } from '../components/dashboard/ChartRangeControls';
import { IconChart, IconClock, IconFrames } from '../components/ui/Icon';
import { EMOTIONS } from '../utils/constants';
import { useSessions } from '../context/SessionsContext';
import { Skeleton } from '../components/ui/Skeleton';

export function Dashboard() {
  const navigate = useNavigate();
  const { sessions, currentSession, selectSession, loading } = useSessions();
  const [range, setRange] = useState('all');

  if (loading || !currentSession) {
    return (
      <div className="stats-row">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} height={92} style={{ borderRadius: 16 }} />
        ))}
      </div>
    );
  }

  const emo = EMOTIONS[currentSession.predominant];

  return (
    <>
      <div className="stats-row">
        <StatCard
          highlight
          label="Emoção Predominante"
          value={emo.label}
          sub={`Confiança: ${currentSession.confidence}%`}
          icon={null}
          iconClassName="emotion-icon"
        />
        <StatCard
          label="Duração do Vídeo"
          value={currentSession.duration}
          icon={<IconClock />}
        />
        <StatCard
          label="Frames Analisados"
          value={currentSession.frames}
          icon={<IconFrames />}
        />
        <StatCard
          label="Total de Sessões"
          value={sessions.length}
          icon={<IconChart />}
        />
      </div>

      <div className="charts-row">
        <Card className="card-probabilities">
          <CardHeader
            title="Probabilidade das Emoções"
            badge="Última sessão"
          />
          <CardBody>
            <ProbabilityList probabilities={currentSession.probabilities} />
          </CardBody>
        </Card>

        <Card className="card-timeline">
          <CardHeader
            title="Emoções ao Longo do Tempo"
            right={<ChartRangeControls range={range} onChange={setRange} />}
          />
          <CardBody className="chart-container">
            <TimelineChart timeline={currentSession.timeline} range={range} />
          </CardBody>
        </Card>
      </div>

      <div className="charts-row">
        <Card className="card-donut">
          <CardHeader title="Distribuição Geral das Emoções" />
          <CardBody>
            <DonutChart probabilities={currentSession.probabilities} />
          </CardBody>
        </Card>

        <Card className="card-recent">
          <CardHeader
            title="Sessões Recentes"
            right={
              <a
                href="#"
                className="card-link"
                onClick={(e) => {
                  e.preventDefault();
                  navigate('/sessions');
                }}
              >
                Ver todas →
              </a>
            }
          />
          <CardBody>
            <MiniSessions
              sessions={sessions}
              onSelect={(s) => {
                selectSession(s);
              }}
            />
          </CardBody>
        </Card>
      </div>
    </>
  );
}
