const statusColors = {
  pending: '#888',
  processing: '#f0a500',
  awaiting_approval: '#5b6af0',
  approved: '#4caf50',
  rejected: '#ff6b6b',
  provisioned: '#00bcd4',
  failed: '#ff6b6b',
}

export default function TaskCard({ task, onClick }) {
  return (
    <div onClick={onClick} style={styles.card}>
      <div style={styles.top}>
        <span style={styles.name}>{task.name}</span>
        <span style={{
          ...styles.status,
          background: statusColors[task.status] + '22',
          color: statusColors[task.status],
          border: `1px solid ${statusColors[task.status]}44`
        }}>
          {task.status.replace(/_/g, ' ')}
        </span>
      </div>
      <p style={styles.desc}>{task.description}</p>
      {task.estimated_cost_usd && (
        <p style={styles.cost}>${task.estimated_cost_usd}/month</p>
      )}
      <p style={styles.date}>{new Date(task.created_at).toLocaleDateString()}</p>
    </div>
  )
}

const styles = {
  card: { background: '#1a1a1a', border: '1px solid #333', borderRadius: '10px', padding: '1rem 1.2rem', marginBottom: '0.8rem', cursor: 'pointer', transition: 'border-color 0.2s' },
  top: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' },
  name: { fontWeight: 500, color: '#fff' },
  status: { fontSize: '0.75rem', padding: '2px 10px', borderRadius: '20px' },
  desc: { color: '#888', fontSize: '0.85rem', margin: '0 0 0.5rem' },
  cost: { color: '#4caf50', fontSize: '0.85rem', margin: '0 0 0.3rem' },
  date: { color: '#555', fontSize: '0.8rem', margin: 0}
}