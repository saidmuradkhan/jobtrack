export const STATUSES = [
  { value: 'wishlist', label: 'Wishlist' },
  { value: 'applied', label: 'Applied' },
  { value: 'interview', label: 'Interview' },
  { value: 'offer', label: 'Offer' },
  { value: 'rejected', label: 'Rejected' },
]

export function statusLabel(value) {
  return STATUSES.find((status) => status.value === value)?.label ?? value
}

export function formatSalary(application) {
  if (application.salary == null) return '—'
  return `${application.salary.toLocaleString()} ${application.currency}`
}
