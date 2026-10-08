import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import ApplicationList from './ApplicationList.jsx'

const application = {
  id: 1,
  company: 'PASHA Bank',
  position: 'Backend developer',
  status: 'interview',
  applied_on: '2026-10-01',
  salary: 3000,
  currency: 'AZN',
  url: 'https://example.com/job',
}

describe('ApplicationList', () => {
  it('shows a row per application with a link to the ad', () => {
    render(<ApplicationList applications={[application]} onEdit={vi.fn()} onDelete={vi.fn()} />)

    const row = screen.getByRole('row', { name: /PASHA Bank/ })
    expect(within(row).getByRole('link', { name: 'Backend developer' })).toHaveAttribute(
      'href',
      'https://example.com/job',
    )
    expect(within(row).getByText('Interview')).toBeInTheDocument()
    expect(within(row).getByText('3,000 AZN')).toBeInTheDocument()
  })

  it('passes the clicked application to edit and delete', async () => {
    const onEdit = vi.fn()
    const onDelete = vi.fn()
    render(<ApplicationList applications={[application]} onEdit={onEdit} onDelete={onDelete} />)

    await userEvent.click(screen.getByRole('button', { name: 'Edit' }))
    await userEvent.click(screen.getByRole('button', { name: 'Delete' }))

    expect(onEdit).toHaveBeenCalledWith(application)
    expect(onDelete).toHaveBeenCalledWith(application)
  })

  it('says so when the list is empty', () => {
    render(<ApplicationList applications={[]} onEdit={vi.fn()} onDelete={vi.fn()} />)
    expect(screen.getByText('No applications found.')).toBeInTheDocument()
  })
})
