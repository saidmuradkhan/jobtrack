import { useEffect, useState } from 'react'
import { getMe, getTokens, logout } from './api.js'
import AuthForm from './components/AuthForm.jsx'
import Dashboard from './components/Dashboard.jsx'
import Vacancies from './components/Vacancies.jsx'

export default function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(Boolean(getTokens()))
  const [tab, setTab] = useState('applications')

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
        <nav className="toggle">
          <button
            className={tab === 'applications' ? 'active' : ''}
            onClick={() => setTab('applications')}
          >
            My applications
          </button>
          <button
            className={tab === 'vacancies' ? 'active' : ''}
            onClick={() => setTab('vacancies')}
          >
            Vacancies
          </button>
        </nav>
        <div className="row">
          <span className="muted">{user.username}</span>
          <button onClick={handleLogout}>Log out</button>
        </div>
      </header>
      {tab === 'applications' ? <Dashboard /> : <Vacancies />}
    </div>
  )
}
