import { describe, expect, it } from 'vitest'
import { convertedSalary } from './rates.js'

const rates = { USD: 1.7, EUR: 1.9048 }

describe('convertedSalary', () => {
  it('shows AZN salaries in dollars', () => {
    expect(convertedSalary(2000, 'AZN', rates)).toBe('≈ $1,176')
  })

  it('shows dollar salaries in manats', () => {
    expect(convertedSalary(3000, 'USD', rates)).toBe('≈ 5,100 AZN')
  })

  it('shows other currencies in both', () => {
    expect(convertedSalary(1000, 'EUR', rates)).toBe('≈ 1,905 AZN · $1,120')
  })

  it('stays empty without a salary, without rates or for an unknown currency', () => {
    expect(convertedSalary(null, 'AZN', rates)).toBe('')
    expect(convertedSalary(2000, 'AZN', null)).toBe('')
    expect(convertedSalary(2000, 'XYZ', rates)).toBe('')
  })
})
