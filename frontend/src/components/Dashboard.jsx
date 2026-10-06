import { useEffect, useState } from 'react'
import {
  createApplication,
  deleteApplication,
  listApplications,
  updateApplication,
} from '../api.js'
import ApplicationForm from './ApplicationForm.jsx'
import ApplicationList from './ApplicationList.jsx'

export default function Dashboard() {
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [editing, setEditing] = useState(null)

  function load() {
    return listApplications()
      .then((data) => {
        setApplications(data)
        setError('')
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [])

  async function handleSave(values) {
    if (editing.id) {
      await updateApplication(editing.id, values)
    } else {
      await createApplication(values)
    }
    setEditing(null)
    await load()
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

  return (
    <>
      <div className="row toolbar">
        <button className="primary" onClick={() => setEditing({})}>
          + Add application
        </button>
      </div>

      {error && <p className="error">{error}</p>}
      {loading ? (
        <p className="muted">Loading…</p>
      ) : (
        <ApplicationList
          applications={applications}
          onEdit={setEditing}
          onDelete={handleDelete}
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
