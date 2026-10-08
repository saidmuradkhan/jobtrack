import { useEffect, useState } from 'react'
import {
  createApplication,
  deleteApplication,
  listApplications,
  updateApplication,
} from '../api.js'
import { useRates } from '../rates.js'
import { STATUSES } from '../statuses.js'
import ApplicationForm from './ApplicationForm.jsx'
import ApplicationList from './ApplicationList.jsx'
import KanbanBoard from './KanbanBoard.jsx'

export default function Dashboard() {
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [editing, setEditing] = useState(null)
  const [view, setView] = useState('list')
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [reloadCount, setReloadCount] = useState(0)
  const rates = useRates()

  useEffect(() => {
    let ignore = false
    const timer = setTimeout(() => {
      listApplications({ search: search.trim(), status })
        .then((data) => {
          if (ignore) return
          setApplications(data)
          setError('')
        })
        .catch((err) => !ignore && setError(err.message))
        .finally(() => !ignore && setLoading(false))
    }, 300)
    return () => {
      ignore = true
      clearTimeout(timer)
    }
  }, [search, status, reloadCount])

  const reload = () => setReloadCount((count) => count + 1)

  async function handleSave(values) {
    if (editing.id) {
      await updateApplication(editing.id, values)
    } else {
      await createApplication(values)
    }
    setEditing(null)
    reload()
  }

  async function handleDelete(application) {
    if (!window.confirm(`Delete "${application.position}" at ${application.company}?`)) return
    try {
      await deleteApplication(application.id)
      setApplications((current) => current.filter((a) => a.id !== application.id))
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleMove(application, newStatus) {
    setApplications((current) =>
      current.map((a) => (a.id === application.id ? { ...a, status: newStatus } : a)),
    )
    try {
      await updateApplication(application.id, { status: newStatus })
    } catch (err) {
      setError(err.message)
      reload()
    }
  }

  return (
    <>
      <div className="row toolbar">
        <input
          type="search"
          placeholder="Search company, position, notes…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="grow"
        />
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">All statuses</option>
          {STATUSES.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>
        <div className="toggle">
          <button className={view === 'list' ? 'active' : ''} onClick={() => setView('list')}>
            List
          </button>
          <button className={view === 'board' ? 'active' : ''} onClick={() => setView('board')}>
            Board
          </button>
        </div>
        <button className="primary" onClick={() => setEditing({})}>
          + Add application
        </button>
      </div>

      {error && <p className="error">{error}</p>}
      {loading ? (
        <p className="muted">Loading…</p>
      ) : view === 'list' ? (
        <ApplicationList
          applications={applications}
          rates={rates}
          onEdit={setEditing}
          onDelete={handleDelete}
        />
      ) : (
        <KanbanBoard
          applications={applications}
          rates={rates}
          onEdit={setEditing}
          onMove={handleMove}
        />
      )}

      {editing && (
        <ApplicationForm
          application={editing}
          onSave={handleSave}
          onCancel={() => setEditing(null)}
        />
      )}
    </>
  )
}
