import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getTask } from '../api/tasks'

const statusColors = {
  pending: '#888', processing: '#f0a500',
  awaiting_approval: '#5b6af0', approved: '#4caf50',
  rejected: '#ff6b6b', provisioned: '#00bcd4', failed: '#ff6b6b'
}

const buildStatusColors = {
  pending: '#555', running: '#f0a500', complete: '#4caf50', failed: '#ff6b6b'
}

export default function TaskDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [task, setTask] = useState(null)

  useEffect(() => {
    fetchTask()
    // poll every 5 seconds while processing
    const interval = setInterval(fetchTask, 5000)
    return () => clearInterval(interval)
  }, [id])

  const fetchTask = async () => {
    try {
      const res = await getTask(id)
      setTask(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  if (!task) return <div style={styles.loading}>Loading...</div>

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <button onClick={() => navigate('/dashboard')} style={styles.back}>← Back</button>
        <h2 style={styles.title}>{task.name}</h2>
        <span style={{
          ...styles.status,
          background: statusColors[task.status] + '22',
          color: statusColors[task.status],
        }}>
          {task.status.replace(/_/g, ' ')}
        </span>
      </div>

      <div style={styles.content}>
        <div style={styles.card}>
          <h3 style={styles.cardTitle}>Request</h3>
          <p style={styles.desc}>{task.description}</p>
          {task.estimated_cost_usd && (
            <p style={styles.cost}>Estimated cost: ${task.estimated_cost_usd}/month</p>
          )}
        </div>

        <div style={styles.card}>
          <h3 style={styles.cardTitle}>Agent Pipeline</h3>
          {['intake', 'classifier', 'blueprint_finder', 'cost_estimator'].map((agent, i) => (
            <div key={agent} style={styles.agentRow}>
              <span style={styles.agentNum}>{i + 1}</span>
              <span style={styles.agentName}>{agent.replace(/_/g, ' ')}</span>
              <span style={{
                ...styles.agentStatus,
                color: task.status === 'pending' ? '#555' :
                       task.status === 'processing' ? '#f0a500' : '#4caf50'
              }}>
                {task.status === 'pending' ? 'waiting' :
                 task.status === 'processing' ? 'running...' : '✓ complete'}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

const styles = {
  container: { minHeight: '100vh', background: '#0f0f0f', color: '#fff' },
  loading: { color: '#888', padding: '2rem', textAlign: 'center' },
  header: { display: 'flex', alignItems: 'center', gap: '1rem', padding: '1.5rem 2rem', borderBottom: '1px solid #333', background: '#1a1a1a' },
  back: { background: 'none', border: '1px solid #444', color: '#ccc', padding: '0.4rem 0.8rem', borderRadius: '8px', cursor: 'pointer' },
  title: { margin: 0, flex: 1 },
  status: { fontSize: '0.8rem', padding: '4px 12px', borderRadius: '20px' },
  content: { maxWidth: '700px', margin: '2rem auto', padding: '0 2rem' },
  card: { background: '#1a1a1a', border: '1px solid #333', borderRadius: '12px', padding: '1.5rem', marginBottom: '1rem' },
  cardTitle: { margin: '0 0 1rem', color: '#ccc' },
  desc: { color: '#888' },
  cost: { color: '#4caf50', marginTop: '0.5rem' },
  agentRow: { display: 'flex', alignItems: 'center', gap: '1rem', padding: '0.6rem 0', borderBottom: '1px solid #222' },
  agentNum: { background: '#333', borderRadius: '50%', width: '24px', height: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem', flexShrink: 0 },
  agentName: { flex: 1, textTransform: 'capitalize' },
  agentStatus: { fontSize: '0.8rem' }
}