import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createApplication, getRates, listVacancies } from '../api.js'
import { vacancyToApplication } from '../vacancies.js'
import Vacancies from './Vacancies.jsx'

vi.mock('../api.js', async (importOriginal) => ({
  ...(await importOriginal()),
  listVacancies: vi.fn(),
  createApplication: vi.fn(),
  getRates: vi.fn(),
}))

const python = {
  uid: 'boss.az:301245',
  source: 'boss.az',
  title: 'Python developer',
  company: 'Kapital Bank',
  url: 'https://boss.az/vacancies/301245',
  location: 'Bakı',
  published_on: '2026-10-07',
  salary_min: 2000,
  salary_max: 3000,
  currency: 'AZN',
  category: 'it',
  tags: ['python'],
  saved: false,
}

const frontend = { ...python, uid: 'jobsearch.az:88812', title: 'Frontend developer', salary_min: null, salary_max: null, saved: true }

describe('Vacancies', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getRates.mockResolvedValue({ date: '2026-10-08', per_unit: { USD: 1.7 } })
    listVacancies.mockResolvedValue({
      count: 2,
      page: 1,
      per_page: 20,
      items: [python, frontend],
      categories: [['it', 2]],
    })
  })

  it('lists vacancies with salaries in AZN and dollars', async () => {
    render(<Vacancies />)

    expect(await screen.findByText('Python developer')).toBeInTheDocument()
    expect(screen.getByText('2,000–3,000 AZN')).toBeInTheDocument()
    expect(await screen.findByText('≈ $1,765')).toBeInTheDocument()
    expect(screen.getByText('Salary not given')).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'it (2)' })).toBeInTheDocument()
  })

  it('saves a vacancy as a wishlist application with one click', async () => {
    createApplication.mockResolvedValue({ id: 7 })
    render(<Vacancies />)

    const [save] = await screen.findAllByRole('button', { name: 'Save' })
    await userEvent.click(save)

    expect(createApplication).toHaveBeenCalledWith(
      expect.objectContaining({
        company: 'Kapital Bank',
        position: 'Python developer',
        status: 'wishlist',
        salary: 3000,
        vacancy_uid: 'boss.az:301245',
      }),
    )
    expect(await screen.findAllByRole('button', { name: 'Saved ✓' })).toHaveLength(2)
  })

  it('searches as you type', async () => {
    render(<Vacancies />)
    await screen.findByText('Python developer')

    await userEvent.type(screen.getByRole('searchbox'), 'django')

    await vi.waitFor(() =>
      expect(listVacancies).toHaveBeenLastCalledWith({ q: 'django', category: '', page: 1 }),
    )
  })
})

describe('vacancyToApplication', () => {
  it('uses the lower salary when only that one is known', () => {
    expect(vacancyToApplication({ ...python, salary_max: null }).salary).toBe(2000)
  })

  it('fills in a company name when the ad has none', () => {
    expect(vacancyToApplication({ ...python, company: '' }).company).toBe('Unknown company')
  })
})
