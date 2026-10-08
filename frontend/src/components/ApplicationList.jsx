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
              <td>
                {application.url ? (
                  <a href={application.url} target="_blank" rel="noreferrer">
                    {application.position}
                  </a>
                ) : (
                  application.position
                )}
              </td>
              <td>{application.company}</td>
              <td>
                <span className={`badge ${application.status}`}>
                  {statusLabel(application.status)}
                </span>
              </td>
              <td>{application.applied_on}</td>
              <td>
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
