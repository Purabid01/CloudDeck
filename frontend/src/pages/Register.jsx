import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { register } from '../api/auth'

export default function Register() {
  const [form, setForm] = useState({ email: '', password: '', full_name: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await register(form)
      navigate('/login')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>Create account</h1>
        <form onSubmit={handleSubmit} style={styles.form}>
          {['full_name', 'email', 'password'].map((field) => (
            <div key={field} style={styles.field}>
              <label style={styles.label}>
                {field.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </label>
              <input
                type={field === 'password' ? 'password' : 'text'}
                name={field}
                value={form[field]}
                onChange={handleChange}
                style={styles.input}
                required
              />
            </div>
          ))}
          {error && <p style={styles.error}>{error}</p>}
          <button type="submit" disabled={loading} style={styles.button}>
            {loading ? 'Creating...' : 'Create account'}
          </button>
        </form>
        <p style={styles.link}>
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  )
}

const styles = {
  container: { minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#0f0f0f' },
  card: { background: '#1a1a1a', padding: '2rem', borderRadius: '12px', width: '100%', maxWidth: '400px', border: '1px solid #333' },
  title: { color: '#fff', marginBottom: '1.5rem' },
  form: { display: 'flex', flexDirection: 'column', gap: '1rem' },
  field: { display: 'flex', flexDirection: 'column', gap: '4px' },
  label: { color: '#ccc', fontSize: '0.9rem' },
  input: { padding: '0.6rem 0.8rem', borderRadius: '8px', border: '1px solid #444', background: '#2a2a2a', color: '#fff', fontSize: '1rem' },
  button: { padding: '0.7rem', borderRadius: '8px', border: 'none', background: '#5b6af0', color: '#fff', fontSize: '1rem', cursor: 'pointer' },
  error: { color: '#ff6b6b', fontSize: '0.9rem' },
  link: { color: '#888', textAlign: 'center', marginTop: '1rem' }
}