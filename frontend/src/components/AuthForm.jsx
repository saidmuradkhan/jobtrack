import { useState } from 'react'
import { login, register } from '../api.js'

export default function AuthForm({ onLoggedIn }) {
  const [mode, setMode] = useState('login')
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const isRegister = mode === 'register'

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setBusy(true)
    try {
      if (isRegister) {
        await register(username, email, password)
      } else {
        await login(username, password)
      }
      onLoggedIn()
    } catch (err) {
      setError(err.status === 401 ? 'Wrong username or password.' : err.message)
    } finally {
      setBusy(false)
    }
  }

  function switchMode() {
    setMode(isRegister ? 'login' : 'register')
    setError('')
  }

  return (
    <div className="auth">
      <h1>jobtrack</h1>
      <p className="muted">Track every job application from wishlist to offer.</p>

      <form className="card form" onSubmit={handleSubmit}>
        <h2>{isRegister ? 'Create an account' : 'Log in'}</h2>

        <label>
          Username
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            required
          />
        </label>

        {isRegister && (
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />
          </label>
        )}

        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete={isRegister ? 'new-password' : 'current-password'}
            required
          />
        </label>

        {error && <p className="error">{error}</p>}

        <button className="primary" disabled={busy}>
          {busy ? 'Please wait…' : isRegister ? 'Sign up' : 'Log in'}
        </button>

        <button type="button" className="link" onClick={switchMode}>
          {isRegister ? 'Already have an account? Log in' : 'No account yet? Sign up'}
        </button>
      </form>
    </div>
  )
}
