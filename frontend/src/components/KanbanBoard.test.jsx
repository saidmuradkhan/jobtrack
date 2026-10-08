import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import KanbanBoard from './KanbanBoard.jsx'

const applications = [
  { id: 1, company: 'Kapital Bank', position: 'QA engineer', status: 'applied', applied_on: '2026-10-01', salary: null, currency: 'AZN' },
  { id: 2, company: 'Azercell', position: 'Data analyst', status: 'applied', applied_on: '2026-10-02', salary: null, currency: 'AZN' },
  { id: 3, company: 'Bakcell', position: 'Frontend developer', status: 'offer', applied_on: '2026-09-20', salary: 2500, currency: 'AZN' },
]

function column(name) {
  return screen.getByRole('heading', { name: new RegExp(name) }).closest('section')
}

function dataTransfer(id) {
  return { getData: () => String(id), setData: vi.fn() }
}

describe('KanbanBoard', () => {
  it('puts each card in the column of its status', () => {
    render(<KanbanBoard applications={applications} onEdit={vi.fn()} onMove={vi.fn()} />)

    expect(column('Applied')).toHaveTextContent('QA engineer')
    expect(column('Applied')).toHaveTextContent('Data analyst')
    expect(column('Offer')).toHaveTextContent('Frontend developer')
    expect(column('Interview')).toHaveTextContent('0')
  })

  it('moves a card when it is dropped on another column', () => {
    const onMove = vi.fn()
    render(<KanbanBoard applications={applications} onEdit={vi.fn()} onMove={onMove} />)

    fireEvent.drop(column('Interview'), { dataTransfer: dataTransfer(1) })

    expect(onMove).toHaveBeenCalledWith(applications[0], 'interview')
  })

  it('ignores a drop on the column the card is already in', () => {
    const onMove = vi.fn()
    render(<KanbanBoard applications={applications} onEdit={vi.fn()} onMove={onMove} />)

    fireEvent.drop(column('Offer'), { dataTransfer: dataTransfer(3) })

    expect(onMove).not.toHaveBeenCalled()
  })
})
