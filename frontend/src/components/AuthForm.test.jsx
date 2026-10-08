import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError, login, register } from '../api.js'
import AuthForm from './AuthForm.jsx'

vi.mock('../api.js', async (importOriginal) => ({
  ...(await importOriginal()),
  login: vi.fn(),
  register: vi.fn(),
}))

describe('AuthForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('logs in and tells the app', async () => {
    const onLoggedIn = vi.fn()
    render(<AuthForm onLoggedIn={onLoggedIn} />)

    await userEvent.type(screen.getByLabelText('Username'), 'said')
    await userEvent.type(screen.getByLabelText('Password'), 's3cure-pass-123')
    await userEvent.click(screen.getByRole('button', { name: 'Log in' }))

    expect(login).toHaveBeenCalledWith('said', 's3cure-pass-123')
    expect(onLoggedIn).toHaveBeenCalled()
  })

  it('shows a friendly message for a wrong password', async () => {
    login.mockRejectedValueOnce(new ApiError(401, { detail: 'No active account' }))
    render(<AuthForm onLoggedIn={vi.fn()} />)

    await userEvent.type(screen.getByLabelText('Username'), 'said')
    await userEvent.type(screen.getByLabelText('Password'), 'wrong')
    await userEvent.click(screen.getByRole('button', { name: 'Log in' }))

    expect(await screen.findByText('Wrong username or password.')).toBeInTheDocument()
  })

  it('switches to sign up and sends the email too', async () => {
    render(<AuthForm onLoggedIn={vi.fn()} />)

    await userEvent.click(screen.getByRole('button', { name: /sign up/i }))
    await userEvent.type(screen.getByLabelText('Username'), 'said')
    await userEvent.type(screen.getByLabelText('Email'), 'said@example.com')
    await userEvent.type(screen.getByLabelText('Password'), 's3cure-pass-123')
    await userEvent.click(screen.getByRole('button', { name: 'Sign up' }))

    expect(register).toHaveBeenCalledWith('said', 'said@example.com', 's3cure-pass-123')
  })
})
