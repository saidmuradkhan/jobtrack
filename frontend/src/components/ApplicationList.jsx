import { convertedSalary } from '../rates.js'
import { formatSalary, statusLabel } from '../statuses.js'

export default function ApplicationList({ applications, rates, onEdit, onDelete }) {
  if (applications.length === 0) {
    return <p className="card muted">No applications found.</p>
  }

  return (
    <div className="card table-wrap">
      <table>
        <thead>
          <tr>
            <th>Position</th>
            <th>Company</th>
            <th>Status</th>
            <th>Applied</th>
            <th>Salary</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {applications.map((application) => (
            <tr key={application.id}>
              <td className="position">
                {application.url ? (
                  <a href={application.url} target="_blank" rel="noreferrer">
                    {application.position}
                  </a>
                ) : (
                  application.position
                )}
              </td>
              <td data-label="Company">{application.company}</td>
              <td data-label="Status">
                <span className={`badge ${application.status}`}>
                  {statusLabel(application.status)}
                </span>
              </td>
              <td data-label="Applied">{application.applied_on}</td>
              <td data-label="Salary">
                {formatSalary(application)}
                <div className="muted small">
                  {convertedSalary(application.salary, application.currency, rates)}
                </div>
              </td>
              <td className="actions">
                <button onClick={() => onEdit(application)}>Edit</button>
                <button className="danger" onClick={() => onDelete(application)}>
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
