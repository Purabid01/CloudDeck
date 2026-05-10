import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getMyTasks, createTask } from '../api/tasks'
import { useAuth } from '../context/AuthContext'
import TaskCard from '../components/TaskCard'

export default function Dashboard() {
  const [tasks, setTasks] = useState([])
  const [description, setDescription] = useState('')
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { member, logoutMember } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    fetchTasks()
  }, [])

  const fetchTasks = async () => {
    try {
      const res = await getMyTasks()
      setTasks(res.data)
    } catch (err) {
      console.error('Failed to fetch tasks', err)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await createTask({ name, description })
      setName('')
      setDescription('')
      fetchTasks()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create task')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
  <h1 style={styles.title}>CloudDeck</h1>
  <div style={styles.headerRight}>
    <button
      onClick={() => navigate('/dashboard')}
      style={{...styles.logoutBtn, background: '#5b6af0', border: '1px solid #5b6af0', color: '#fff'}}
    >
      My Requests
    </button>
    <button
      onClick={() => navigate('/approvals')}
      style={styles.logoutBtn}
    >
      Approvals
    </button>
    <span style={styles.email}>{member?.email}</span>
    <button onClick={logoutMember} style={styles.logoutBtn}>Logout</button>
  </div>
</div>

      <div style={styles.content}>
        {/* New Task Form */}
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>What would you like to build?</h2>
          <p style={styles.cardSub}>Describe what you need in plain English</p>
          <form onSubmit={handleSubmit} style={styles.form}>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              style={styles.input}
              placeholder="Give it a name e.g. Flight Price Portal"
              required
            />
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              style={styles.textarea}
              placeholder="I need a dashboard to analyze customer behaviour..."
              rows={3}
              required
            />
            {error && <p style={styles.error}>{error}</p>}
            <button type="submit" disabled={loading} style={styles.button}>
              {loading ? 'Submitting...' : 'Submit request'}
            </button>
          </form>
        </div>

        {/* Task List */}
        <div style={styles.taskList}>
          <h2 style={styles.sectionTitle}>My requests</h2>
          {tasks.length === 0 ? (
            <p style={styles.empty}>No requests yet. Submit one above.</p>
          ) : (
            tasks.map(task => (
              <TaskCard
                key={task.id}
                task={task}
                onClick={() => navigate(`/tasks/${task.id}`)}
              />
            ))
          )}
        </div>
      </div>
    </div>
  )
}

const styles = {
  container: { minHeight: '100vh', background: '#0f0f0f', color: '#fff' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 2rem', borderBottom: '1px solid #333', background: '#1a1a1a' },
  title: { margin: 0, color: '#5b6af0' },
  headerRight: { display: 'flex', alignItems: 'center', gap: '1rem' },
  email: { color: '#888', fontSize: '0.9rem' },
  logoutBtn: { padding: '0.4rem 1rem', borderRadius: '8px', border: '1px solid #444', background: 'transparent', color: '#ccc', cursor: 'pointer' },
  content: { maxWidth: '800px', margin: '0 auto', padding: '2rem' },
  card: { background: '#1a1a1a', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333', marginBottom: '2rem' },
  cardTitle: { margin: '0 0 4px', fontSize: '1.2rem' },
  cardSub: { color: '#888', margin: '0 0 1rem', fontSize: '0.9rem' },
  form: { display: 'flex', flexDirection: 'column', gap: '0.8rem' },
  input: { padding: '0.6rem 0.8rem', borderRadius: '8px', border: '1px solid #444', background: '#2a2a2a', color: '#fff', fontSize: '1rem' },
  textarea: { padding: '0.6rem 0.8rem', borderRadius: '8px', border: '1px solid #444', background: '#2a2a2a', color: '#fff', fontSize: '1rem', resize: 'vertical' },
  button: { padding: '0.7rem', borderRadius: '8px', border: 'none', background: '#5b6af0', color: '#fff', fontSize: '1rem', cursor: 'pointer' },
  error: { color: '#ff6b6b', fontSize: '0.9rem' },
  taskList: { marginTop: '1rem' },
  sectionTitle: { color: '#ccc', marginBottom: '1rem' },
  empty: { color: '#555', textAlign: 'center', padding: '2rem' }
}