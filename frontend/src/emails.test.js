import { describe, expect, it } from 'vitest'
import { describeEmail, guessLabel } from './emails.js'

const application = { id: 3, company: 'Acme Bank', position: 'Backend Developer', status: 'interview' }

describe('describeEmail', () => {
  it('says what happened to the application', () => {
    expect(describeEmail({ outcome: 'created', application })).toBe(
      'Added Backend Developer at Acme Bank',
    )
    expect(
      describeEmail({ outcome: 'updated', application, previous_status: 'applied', status: 'interview' }),
    ).toBe('Backend Developer at Acme Bank: Applied → Interview')
    expect(describeEmail({ outcome: 'unchanged', application })).toBe(
      'Backend Developer at Acme Bank: no change',
    )
    expect(describeEmail({ outcome: 'ignored', application: null })).toBe('Not about a job, skipped')
  })
})

describe('guessLabel', () => {
  it('shows what we read from the email', () => {
    expect(guessLabel({ company: 'Contoso', position: 'Data Engineer', status: 'offer' })).toBe(
      'Data Engineer at Contoso → Offer',
    )
    expect(guessLabel({ company: '', position: '', status: 'applied' })).toBe(
      'Unknown company → Applied',
    )
  })
})
