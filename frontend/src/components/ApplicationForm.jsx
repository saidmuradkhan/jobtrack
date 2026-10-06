import { useState } from 'react'
import { STATUSES } from '../statuses.js'

const today = () => new Date().toISOString().slice(0, 10)

function initialValues(application) {
  return {
    company: application?.company ?? '',
    position: application?.position ?? '',
    status: application?.status ?? 'applied',
    applied_on: application?.applied_on ?? today(),
    salary: application?.salary ?? '',
    currency: application?.currency ?? 'AZN',
    url: application?.url ?? '',
    notes: application?.notes ?? '',
  }
}

export default function ApplicationForm({ application, onSave, onCancel }) {
  const [values, setValues] = useState(() => initialValues(application))
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  function handleChange(event) {
    const { name, value } = event.target
    setValues((current) => ({ ...current, [name]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setBusy(true)
    try {
      await onSave({ ...values, salary: values.salary === '' ? null : Number(values.salary) })
    } catch (err) {
      setError(err.message)
      setBusy(false)
    }
  }

  return (
    <div className="overlay" onClick={onCancel}>
      <form
        className="card form dialog"
        onSubmit={handleSubmit}
        onClick={(e) => e.stopPropagation()}
      >
        <h2>{application?.id ? 'Edit application' : 'New application'}</h2>

        <div className="grid">
          <label>
            Company
            <input name="company" value={values.company} onChange={handleChange} required />
          </label>
          <label>
            Position
            <input name="position" value={values.position} onChange={handleChange} required />
          </label>
          <label>
            Status
            <select name="status" value={values.status} onChange={handleChange}>
              {STATUSES.map((status) => (
                <option key={status.value} value={status.value}>
                  {status.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Applied on
            <input
              type="date"
              name="applied_on"
              value={values.applied_on}
              onChange={handleChange}
              required
            />
          </label>
          <label>
            Salary
            <input
              type="number"
              min="0"
              name="salary"
              value={values.salary}
              onChange={handleChange}
            />
          </label>
          <label>
            Currency
            <input
              name="currency"
              value={values.currency}
              onChange={handleChange}
              maxLength={3}
              required
            />
          </label>
        </div>

        <label>
          Link
          <input type="url" name="url" value={values.url} onChange={handleChange} />
        </label>
        <label>
          Notes
          <textarea name="notes" rows={4} value={values.notes} onChange={handleChange} />
        </label>

        {error && <p className="error">{error}</p>}

        <div className="row end">
          <button type="button" onClick={onCancel}>
            Cancel
          </button>
          <button className="primary" disabled={busy}>
            {busy ? 'Saving…' : 'Save'}
          </button>
        </div>
      </form>
    </div>
  )
}
