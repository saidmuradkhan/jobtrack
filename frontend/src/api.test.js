import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { getTokens, listApplications, login } from './api.js'

function reply(status, body) {
  return Promise.resolve(new Response(JSON.stringify(body), { status }))
}

describe('api', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('stores both tokens after logging in', async () => {
    fetch.mockReturnValueOnce(reply(200, { access: 'a1', refresh: 'r1' }))
    await login('said', 'secret')
    expect(getTokens()).toEqual({ access: 'a1', refresh: 'r1' })
  })

  it('sends the access token with each request', async () => {
    localStorage.setItem('jobtrack.tokens', JSON.stringify({ access: 'a1', refresh: 'r1' }))
    fetch.mockReturnValueOnce(reply(200, []))

    await listApplications({ status: 'offer', search: 'pasha' })

    const [url, options] = fetch.mock.calls[0]
    expect(url).toBe('/api/applications/?status=offer&search=pasha')
    expect(options.headers.Authorization).toBe('Bearer a1')
  })

  it('gets a new access token once and repeats the request after a 401', async () => {
    localStorage.setItem('jobtrack.tokens', JSON.stringify({ access: 'old', refresh: 'r1' }))
    fetch
      .mockReturnValueOnce(reply(401, { detail: 'Token expired' }))
      .mockReturnValueOnce(reply(200, { access: 'new' }))
      .mockReturnValueOnce(reply(200, [{ id: 1 }]))

    expect(await listApplications()).toEqual([{ id: 1 }])
    expect(fetch.mock.calls[2][1].headers.Authorization).toBe('Bearer new')
    expect(getTokens().access).toBe('new')
  })

  it('logs out when the refresh token is no longer valid', async () => {
    localStorage.setItem('jobtrack.tokens', JSON.stringify({ access: 'old', refresh: 'expired' }))
    fetch
      .mockReturnValueOnce(reply(401, { detail: 'Token expired' }))
      .mockReturnValueOnce(reply(401, { detail: 'Token is invalid' }))

    await expect(listApplications()).rejects.toThrow('Token expired')
    expect(getTokens()).toBeNull()
  })
})
