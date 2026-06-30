import { ConfidenceBar } from '../ui/ConfidenceBar';
import { EmotionTag } from '../ui/EmotionTag';
import { formatDate } from '../../utils/formatters';

export function SessionsTable({ sessions, onSelect, loading }) {
  if (loading) {
    return (
      <div className="empty-state">Carregando sessões...</div>
    );
  }
  if (!sessions.length) {
    return (
      <div className="empty-state">
        Nenhuma sessão encontrada. Faça upload de um vídeo para começar.
      </div>
    );
  }
  return (
    <table className="sessions-table">
      <thead>
        <tr>
          <th>Sessão</th>
          <th>Data</th>
          <th>Duração</th>
          <th>Emoção Principal</th>
          <th>Confiança</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        {sessions.map((s) => (
          <tr key={s.id}>
            <td><strong>{s.name}</strong></td>
            <td>{formatDate(s.date)}</td>
            <td>{s.duration}</td>
            <td><EmotionTag emotion={s.predominant} /></td>
            <td><ConfidenceBar value={s.confidence} /></td>
            <td>
              <button
                type="button"
                className="btn-table-action"
                onClick={() => onSelect(s)}
              >
                Ver detalhes
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
