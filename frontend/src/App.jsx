import { useEffect, useState } from 'react'
import { getMe, getTokens, logout } from './api.js'
import AuthForm from './components/AuthForm.jsx'
import Dashboard from './components/Dashboard.jsx'

export default function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(Boolean(getTokens()))

  function loadUser() {
    getMe()
      .then(setUser)
      .catch(() => {
        logout()
        setUser(null)
      })
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    if (getTokens()) loadUser()
  }, [])

  function handleLogout() {
    logout()
    setUser(null)
  }

  if (loading) return <p className="page muted">Loading…</p>
  if (!user) return <AuthForm onLoggedIn={loadUser} />

  return (
    <div className="page">
      <header className="topbar">
        <h1>jobtrack</h1>
        <div className="row">
          <span className="muted">{user.username}</span>
          <button onClick={handleLogout}>Log out</button>
        </div>
      </header>
      <Dashboard />
    </div>
  )
}
