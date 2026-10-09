const today = () => new Date().toISOString().slice(0, 10)

export function salaryRange({ salary_min: min, salary_max: max, currency }) {
  const amount = (value) => Math.round(value).toLocaleString('en-US')
  if (min != null && max != null && min !== max) return `${amount(min)}–${amount(max)} ${currency}`
  if (max != null) return `up to ${amount(max)} ${currency}`
  if (min != null) return `from ${amount(min)} ${currency}`
  return 'Salary not given'
}

export function vacancyToApplication(vacancy) {
  const salary = vacancy.salary_max ?? vacancy.salary_min
  return {
    company: (vacancy.company || 'Unknown company').slice(0, 200),
    position: vacancy.title.slice(0, 200),
    status: 'wishlist',
    applied_on: today(),
    salary: salary == null ? null : Math.round(salary),
    currency: vacancy.currency,
    url: vacancy.url,
    notes: `Saved from ${vacancy.source}`,
    vacancy_uid: vacancy.uid,
  }
}
