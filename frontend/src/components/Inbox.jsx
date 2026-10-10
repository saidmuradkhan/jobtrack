import { useEffect, useState } from 'react'
import { acceptEmail, dismissEmail, getInbox, listApplications } from '../api.js'
import { GMAIL_FILTER, describeEmail, guessLabel } from '../emails.js'

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)

  async function copy() {
    await navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return <button onClick={copy}>{copied ? 'Copied ✓' : 'Copy'}</button>
}

function PendingEmail({ email, applications, onAnswer }) {
  const [choice, setChoice] = useState(email.company ? 'new' : '')
  const [busy, setBusy] = useState(false)

  async function answer(action) {
    setBusy(true)
    try {
      await onAnswer(email, action, choice === 'new' ? null : Number(choice))
    } finally {
      setBusy(false)
    }
  }

  return (
    <li className="card email">
      <strong>{guessLabel(email)}</strong>
      <div className="muted small">
        {email.sender} · {email.subject}
      </div>
      {email.snippet && <p className="small">{email.snippet}</p>}
      <div className="row">
        <select value={choice} onChange={(e) => setChoice(e.target.value)} aria-label="Application">
          {!email.company && <option value="">Which application is this about?</option>}
          {email.company && <option value="new">Add as a new application</option>}
          {applications.map((app) => (
            <option key={app.id} value={app.id}>
              {app.position} at {app.company}
            </option>
          ))}
        </select>
        <button className="primary" disabled={busy || !choice} onClick={() => answer('accept')}>
          Confirm
        </button>
        <button disabled={busy} onClick={() => answer('dismiss')}>
          Dismiss
        </button>
      </div>
    </li>
  )
}

export default function Inbox() {
  const [inbox, setInbox] = useState(null)
  const [applications, setApplications] = useState([])
  const [error, setError] = useState('')
  const [reloadCount, setReloadCount] = useState(0)

  useEffect(() => {
    let ignore = false
    Promise.all([getInbox(), listApplications()])
      .then(([inboxData, applicationData]) => {
        if (ignore) return
        setInbox(inboxData)
        setApplications(applicationData)
        setError('')
      })
      .catch((err) => !ignore && setError(err.message))
    return () => {
      ignore = true
    }
  }, [reloadCount])

  async function handleAnswer(email, action, applicationId) {
    try {
      if (action === 'accept') await acceptEmail(email.id, applicationId)
      else await dismissEmail(email.id)
      setReloadCount((count) => count + 1)
    } catch (err) {
      setError(err.message)
    }
  }

  if (!inbox) return error ? <p className="error">{error}</p> : <p className="muted">Loading…</p>

  const pending = inbox.emails.filter((email) => email.outcome === 'pending')
  const handled = inbox.emails.filter((email) => email.outcome !== 'pending')
  const confirmation = inbox.forwarding_confirmation

  return (
    <div className="inbox">
      {error && <p className="error">{error}</p>}

      <section className="card">
        <h2>Forward job emails to jobtrack</h2>
        <p className="muted">
          Applications, interview invitations, offers and rejections sent to this address update
          your list by themselves. Only the emails your filter forwards ever reach us.
        </p>
        <div className="row">
          <code className="grow address">{inbox.address}</code>
          <CopyButton text={inbox.address} />
        </div>

        {confirmation && (
          <p className="notice">
            Gmail confirmation code: <strong>{confirmation.forwarding_code}</strong>
            {confirmation.forwarding_link && (
              <>
                {' '}
                · <a href={confirmation.forwarding_link} target="_blank" rel="noreferrer">
                  Confirm in Gmail
                </a>
              </>
            )}
          </p>
        )}

        <details>
          <summary>How to set it up in Gmail</summary>
          <ol>
            <li>
              Gmail → Settings → <em>Forwarding and POP/IMAP</em> → <em>Add a forwarding
              address</em> → paste the address above.
            </li>
            <li>Gmail sends a confirmation code. It shows up on this page within a minute.</li>
            <li>
              Keep forwarding <em>disabled</em> there. Instead create a filter (search box → show
              search options) with this search, choose <em>Create filter</em> → <em>Forward it
              to</em> your jobtrack address:
              <div className="row">
                <code className="grow">{GMAIL_FILTER}</code>
                <CopyButton text={GMAIL_FILTER} />
              </div>
            </li>
          </ol>
          <p className="muted small">
            Older emails are not imported. Add applications you already sent by hand once, and
            later emails about them will keep their status up to date.
          </p>
        </details>
      </section>

      {pending.length > 0 && (
        <section>
          <h3>Please check ({pending.length})</h3>
          <ul className="emails">
            {pending.map((email) => (
              <PendingEmail
                key={email.id}
                email={email}
                applications={applications}
                onAnswer={handleAnswer}
              />
            ))}
          </ul>
        </section>
      )}

      <section>
        <h3>Recent updates</h3>
        {handled.length === 0 ? (
          <p className="muted">No forwarded emails yet.</p>
        ) : (
          <ul className="emails">
            {handled.map((email) => (
              <li key={email.id} className={`card email ${email.outcome}`}>
                <strong>{describeEmail(email)}</strong>
                <div className="muted small">
                  {new Date(email.received_at).toLocaleDateString()} · {email.subject}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
