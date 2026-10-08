import { useState } from 'react'
import { convertedSalary } from '../rates.js'
import { STATUSES, formatSalary } from '../statuses.js'

export default function KanbanBoard({ applications, rates, onEdit, onMove }) {
  const [dropTarget, setDropTarget] = useState(null)

  function handleDrop(event, status) {
    event.preventDefault()
    setDropTarget(null)
    const id = Number(event.dataTransfer.getData('text/plain'))
    const application = applications.find((a) => a.id === id)
    if (application && application.status !== status) onMove(application, status)
  }

  return (
    <div className="board">
      {STATUSES.map((status) => {
        const cards = applications.filter((a) => a.status === status.value)
        return (
          <section
            key={status.value}
            className={`column ${dropTarget === status.value ? 'drop-target' : ''}`}
            onDragOver={(e) => {
              e.preventDefault()
              setDropTarget(status.value)
            }}
            onDragLeave={() => setDropTarget(null)}
            onDrop={(e) => handleDrop(e, status.value)}
          >
            <h3>
              <span className={`badge ${status.value}`}>{status.label}</span>
              <span className="muted"> {cards.length}</span>
            </h3>
            {cards.map((application) => (
              <article
                key={application.id}
                className="card kanban-card"
                draggable
                onDragStart={(e) => e.dataTransfer.setData('text/plain', String(application.id))}
                onClick={() => onEdit(application)}
              >
                <strong>{application.position}</strong>
                <span>{application.company}</span>
                <span className="muted">
                  {application.applied_on} · {formatSalary(application)}
                </span>
                {application.salary != null && rates && (
                  <span className="muted small">
                    {convertedSalary(application.salary, application.currency, rates)}
                  </span>
                )}
              </article>
            ))}
          </section>
        )
      })}
    </div>
  )
}
