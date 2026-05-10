import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getPendingReviews, decideReview } from '../api/tasks'
import { useAuth } from '../context/AuthContext'

export default function Approvals() {
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [deciding, setDeciding] = useState(null)
  const [rejectionReason, setRejectionReason] = useState('')
  const { member, logoutMember } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    fetchReviews()
  }, [])

  const fetchReviews = async () => {
    try {
      const res = await getPendingReviews()
      setReviews(res.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleDecision = async (taskId, approved) => {
    if (!approved && !rejectionReason) {
      alert('Please provide a rejection reason')
      return
    }
    setDeciding(taskId)
    try {
      await decideReview(taskId, {
        approved,
        rejection_reason: approved ? null : rejectionReason
      })
      fetchReviews()
      setRejectionReason('')
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to decide')
    } finally {
      setDeciding(null)
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>CloudDeck</h1>
        <div style={styles.headerRight}>
          <button 
            onClick={() => navigate('/dashboard')} 
            style={styles.navBtn}
          >
            My Requests
          </button>
          <button 
            onClick={() => navigate('/approvals')} 
            style={{...styles.navBtn, ...styles.navBtnActive}}
          >
            Approvals
          </button>
          <span style={styles.email}>{member?.email}</span>
          <button onClick={logoutMember} style={styles.logoutBtn}>
            Logout
          </button>
        </div>
      </div>

      <div style={styles.content}>
        <h2 style={styles.sectionTitle}>
          Pending Approvals 
          {reviews.length > 0 && (
            <span style={styles.badge}>{reviews.length}</span>
          )}
        </h2>

        {loading && <p style={styles.empty}>Loading...</p>}

        {!loading && reviews.length === 0 && (
          <p style={styles.empty}>No pending approvals. All caught up!</p>
        )}

        {reviews.map(review => (
          <div key={review.id} style={styles.card}>
            <div style={styles.cardTop}>
              <div>
                <p style={styles.taskId}>Task ID: {review.task_id}</p>
                <p style={styles.submitted}>
                  Submitted: {new Date(review.created_at).toLocaleString()}
                </p>
              </div>
              <span style={styles.pendingBadge}>pending review</span>
            </div>

            <div style={styles.actions}>
              <input
                placeholder="Rejection reason (required if rejecting)"
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                style={styles.input}
              />
              <div style={styles.buttons}>
                <button
                  onClick={() => handleDecision(review.task_id, false)}
                  disabled={deciding === review.task_id}
                  style={styles.rejectBtn}
                >
                  Reject
                </button>
                <button
                  onClick={() => handleDecision(review.task_id, true)}
                  disabled={deciding === review.task_id}
                  style={styles.approveBtn}
                >
                  {deciding === review.task_id ? 'Processing...' : 'Approve'}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

const styles = {
  container: { minHeight: '100vh', background: '#0f0f0f', color: '#fff' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 2rem', borderBottom: '1px solid #333', background: '#1a1a1a' },
  title: { margin: 0, color: '#5b6af0' },
  headerRight: { display: 'flex', alignItems: 'center', gap: '1rem' },
  navBtn: { padding: '0.4rem 1rem', borderRadius: '8px', border: '1px solid #444', background: 'transparent', color: '#ccc', cursor: 'pointer' },
  navBtnActive: { background: '#5b6af0', border: '1px solid #5b6af0', color: '#fff' },
  email: { color: '#888', fontSize: '0.9rem' },
  logoutBtn: { padding: '0.4rem 1rem', borderRadius: '8px', border: '1px solid #444', background: 'transparent', color: '#ccc', cursor: 'pointer' },
  content: { maxWidth: '800px', margin: '2rem auto', padding: '0 2rem' },
  sectionTitle: { display: 'flex', alignItems: 'center', gap: '0.8rem', marginBottom: '1.5rem' },
  badge: { background: '#5b6af0', borderRadius: '20px', padding: '2px 10px', fontSize: '0.8rem' },
  empty: { color: '#555', textAlign: 'center', padding: '3rem' },
  card: { background: '#1a1a1a', border: '1px solid #333', borderRadius: '12px', padding: '1.5rem', marginBottom: '1rem' },
  cardTop: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' },
  taskId: { color: '#888', fontSize: '0.85rem', margin: '0 0 4px', fontFamily: 'monospace' },
  submitted: { color: '#555', fontSize: '0.8rem', margin: 0 },
  pendingBadge: { background: '#5b6af022', color: '#5b6af0', border: '1px solid #5b6af044', borderRadius: '20px', padding: '2px 10px', fontSize: '0.75rem' },
  actions: { display: 'flex', flexDirection: 'column', gap: '0.8rem' },
  input: { padding: '0.6rem 0.8rem', borderRadius: '8px', border: '1px solid #444', background: '#2a2a2a', color: '#fff', fontSize: '0.9rem', width: '100%' },
  buttons: { display: 'flex', gap: '0.8rem', justifyContent: 'flex-end' },
  rejectBtn: { padding: '0.6rem 1.5rem', borderRadius: '8px', border: '1px solid #ff6b6b', background: 'transparent', color: '#ff6b6b', cursor: 'pointer', fontSize: '0.9rem' },
  approveBtn: { padding: '0.6rem 1.5rem', borderRadius: '8px', border: 'none', background: '#4caf50', color: '#fff', cursor: 'pointer', fontSize: '0.9rem' },
}