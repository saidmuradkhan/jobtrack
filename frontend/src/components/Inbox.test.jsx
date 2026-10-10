import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { acceptEmail, dismissEmail, getInbox, listApplications } from '../api.js'
import Inbox from './Inbox.jsx'

vi.mock('../api.js', async (importOriginal) => ({
  ...(await importOriginal()),
  getInbox: vi.fn(),
  listApplications: vi.fn(),
  acceptEmail: vi.fn(),
  dismissEmail: vi.fn(),
}))

const acme = { id: 3, company: 'Acme Bank', position: 'Backend Developer', status: 'interview' }

const offer = {
  id: 11,
  sender: 'Contoso People <people@contoso.example>',
  subject: 'Your offer from Contoso',
  snippet: 'We are pleased to offer you the position…',
  status: 'offer',
  company: 'Contoso',
  position: 'Data Engineer',
  outcome: 'pending',
  previous_status: '',
  application: null,
  received_at: '2026-10-15T12:00:00Z',
}

const interview = {
  ...offer,
  id: 10,
  subject: 'Müsahibə dəvəti',
  status: 'interview',
  company: 'Acme Bank',
  outcome: 'updated',
  previous_status: 'applied',
  application: acme,
}

function inbox(overrides = {}) {
  return {
    address: 'said-ab12cd34ef@in.jobs.saidmuradkhan.dev',
    forwarding_confirmation: null,
    pending: 1,
    emails: [offer, interview],
    ...overrides,
  }
}

describe('Inbox', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getInbox.mockResolvedValue(inbox())
    listApplications.mockResolvedValue([acme])
    acceptEmail.mockResolvedValue({})
    dismissEmail.mockResolvedValue({})
  })

  it('shows the address, what changed and what needs a look', async () => {
    render(<Inbox />)
    expect(await screen.findByText('said-ab12cd34ef@in.jobs.saidmuradkhan.dev')).toBeInTheDocument()
    expect(screen.getByText('Backend Developer at Acme Bank: Applied → Interview')).toBeInTheDocument()
    expect(screen.getByText('Please check (1)')).toBeInTheDocument()
    expect(screen.getByText('Data Engineer at Contoso → Offer')).toBeInTheDocument()
  })

  it('adds an unsure email as a new application', async () => {
    render(<Inbox />)
    await userEvent.click(await screen.findByRole('button', { name: 'Confirm' }))
    expect(acceptEmail).toHaveBeenCalledWith(11, null)
    expect(getInbox).toHaveBeenCalledTimes(2)
  })

  it('links an unsure email to an existing application', async () => {
    render(<Inbox />)
    await userEvent.selectOptions(await screen.findByLabelText('Application'), '3')
    await userEvent.click(screen.getByRole('button', { name: 'Confirm' }))
    expect(acceptEmail).toHaveBeenCalledWith(11, 3)
  })

  it('dismisses an email', async () => {
    render(<Inbox />)
    await userEvent.click(await screen.findByRole('button', { name: 'Dismiss' }))
    expect(dismissEmail).toHaveBeenCalledWith(11)
  })

  it('asks which application when the company is unknown', async () => {
    getInbox.mockResolvedValue(inbox({ emails: [{ ...offer, company: '' }] }))
    render(<Inbox />)
    expect(await screen.findByRole('button', { name: 'Confirm' })).toBeDisabled()
    expect(screen.queryByText('Add as a new application')).not.toBeInTheDocument()
  })

  it('shows the Gmail confirmation code', async () => {
    getInbox.mockResolvedValue(
      inbox({
        forwarding_confirmation: {
          forwarding_code: '482913775',
          forwarding_link: 'https://mail-settings.google.com/mail/vf-x',
          received_at: '2026-10-11T07:00:00Z',
        },
      }),
    )
    render(<Inbox />)
    expect(await screen.findByText('482913775')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Confirm in Gmail' })).toHaveAttribute(
      'href',
      'https://mail-settings.google.com/mail/vf-x',
    )
  })
})
