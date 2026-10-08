import { describe, expect, it } from 'vitest'
import { formatSalary, statusLabel } from './statuses.js'

describe('statusLabel', () => {
  it('turns a status value into its label', () => {
    expect(statusLabel('interview')).toBe('Interview')
  })

  it('falls back to the raw value for unknown statuses', () => {
    expect(statusLabel('ghosted')).toBe('ghosted')
  })
})

describe('formatSalary', () => {
  it('shows the amount with its currency', () => {
    expect(formatSalary({ salary: 2500, currency: 'AZN' })).toBe('2,500 AZN')
  })

  it('shows a dash when there is no salary', () => {
    expect(formatSalary({ salary: null, currency: 'AZN' })).toBe('—')
  })
})
