import { useEffect, useState } from 'react'
import { createApplication, listVacancies } from '../api.js'
import { convertedSalary, useRates } from '../rates.js'
import { salaryRange, vacancyToApplication } from '../vacancies.js'

export default function Vacancies() {
  const rates = useRates()
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('')
  const [page, setPage] = useState(1)
  const [data, setData] = useState(null)
  const [categories, setCategories] = useState([])
  const [error, setError] = useState('')
  const [savingUid, setSavingUid] = useState(null)

  useEffect(() => {
    let ignore = false
    const timer = setTimeout(() => {
      listVacancies({ q: query.trim(), category, page })
        .then((result) => {
          if (ignore) return
          setData(result)
          setError('')
          if (!category) setCategories(result.categories)
        })
        .catch((err) => !ignore && setError(err.message))
    }, 300)
    return () => {
      ignore = true
      clearTimeout(timer)
    }
  }, [query, category, page])

  async function handleSave(vacancy) {
    setSavingUid(vacancy.uid)
    try {
      await createApplication(vacancyToApplication(vacancy))
      setData((current) => ({
        ...current,
        items: current.items.map((v) => (v.uid === vacancy.uid ? { ...v, saved: true } : v)),
      }))
    } catch (err) {
      setError(err.message)
    } finally {
      setSavingUid(null)
    }
  }

  const pages = data ? Math.max(1, Math.ceil(data.count / data.per_page)) : 1

  return (
    <>
      <div className="row toolbar">
        <input
          type="search"
          placeholder="Search vacancies: python, accountant, Kapital Bank…"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            setPage(1)
          }}
          className="grow"
        />
        <select
          value={category}
          onChange={(e) => {
            setCategory(e.target.value)
            setPage(1)
          }}
          aria-label="Category"
        >
          <option value="">All categories</option>
          {categories.map(([value, count]) => (
            <option key={value} value={value}>
              {value} ({count})
            </option>
          ))}
        </select>
      </div>

      {error && <p className="error">{error}</p>}
      {!data ? (
        !error && <p className="muted">Loading vacancies…</p>
      ) : data.items.length === 0 ? (
        <p className="card muted">No vacancies match.</p>
      ) : (
        <>
          <p className="muted">
            {data.count.toLocaleString('en-US')} vacancies from Azerbaijani job sites, collected by
            az-job-radar
          </p>
          <ul className="vacancies">
            {data.items.map((vacancy) => (
              <li key={vacancy.uid} className="card vacancy">
                <div className="grow">
                  <a href={vacancy.url} target="_blank" rel="noreferrer">
                    <strong>{vacancy.title}</strong>
                  </a>
                  <div>{vacancy.company}</div>
                  <div className="muted small">
                    {[vacancy.location, vacancy.source, vacancy.published_on].filter(Boolean).join(' · ')}
                  </div>
                  <div className="small">
                    {salaryRange(vacancy)}{' '}
                    <span className="muted">
                      {convertedSalary(vacancy.salary_max ?? vacancy.salary_min, vacancy.currency, rates)}
                    </span>
                  </div>
                </div>
                <button
                  className={vacancy.saved ? '' : 'primary'}
                  disabled={vacancy.saved || savingUid === vacancy.uid}
                  onClick={() => handleSave(vacancy)}
                >
                  {vacancy.saved ? 'Saved ✓' : savingUid === vacancy.uid ? 'Saving…' : 'Save'}
                </button>
              </li>
            ))}
          </ul>
          <div className="row end">
            <button disabled={page <= 1} onClick={() => setPage(page - 1)}>
              ← Previous
            </button>
            <span className="muted">
              Page {page} of {pages}
            </span>
            <button disabled={page >= pages} onClick={() => setPage(page + 1)}>
              Next →
            </button>
          </div>
        </>
      )}
    </>
  )
}
