const API_URL = import.meta.env.VITE_API_URL ?? ''
const TOKENS_KEY = 'jobtrack.tokens'

export class ApiError extends Error {
  constructor(status, data) {
    super(firstErrorMessage(data) ?? `Request failed (${status})`)
    this.status = status
    this.data = data
  }
}

function firstErrorMessage(data) {
  if (!data || typeof data !== 'object') return null
  if (data.detail) return data.detail
  const [field, messages] = Object.entries(data)[0] ?? []
  if (!field) return null
  const message = Array.isArray(messages) ? messages[0] : messages
  return field === 'non_field_errors' ? message : `${field}: ${message}`
}

export function getTokens() {
  try {
    return JSON.parse(localStorage.getItem(TOKENS_KEY))
  } catch {
    return null
  }
}

function saveTokens(tokens) {
  localStorage.setItem(TOKENS_KEY, JSON.stringify(tokens))
}

export function logout() {
  localStorage.removeItem(TOKENS_KEY)
}

async function send(path, { method = 'GET', body, token } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers.Authorization = `Bearer ${token}`

  const response = await fetch(API_URL + path, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  const data = response.status === 204 ? null : await response.json().catch(() => null)
  if (!response.ok) throw new ApiError(response.status, data)
  return data
}

async function refreshAccessToken() {
  const tokens = getTokens()
  if (!tokens?.refresh) return null
  try {
    const { access } = await send('/api/auth/token/refresh/', {
      method: 'POST',
      body: { refresh: tokens.refresh },
    })
    saveTokens({ ...tokens, access })
    return access
  } catch {
    logout()
    return null
  }
}

async function request(path, options = {}) {
  try {
    return await send(path, { ...options, token: getTokens()?.access })
  } catch (error) {
    if (error.status !== 401) throw error
    const access = await refreshAccessToken()
    if (!access) throw error
    return send(path, { ...options, token: access })
  }
}

export async function login(username, password) {
  const tokens = await send('/api/auth/token/', {
    method: 'POST',
    body: { username, password },
  })
  saveTokens(tokens)
}

export async function register(username, email, password) {
  await send('/api/auth/register/', {
    method: 'POST',
    body: { username, email, password },
  })
  await login(username, password)
}

export function getMe() {
  return request('/api/auth/me/')
}

export function listApplications({ status, search } = {}) {
  const params = new URLSearchParams()
  if (status) params.set('status', status)
  if (search) params.set('search', search)
  const query = params.toString()
  return request(`/api/applications/${query ? `?${query}` : ''}`)
}

export function createApplication(data) {
  return request('/api/applications/', { method: 'POST', body: data })
}

export function updateApplication(id, data) {
  return request(`/api/applications/${id}/`, { method: 'PATCH', body: data })
}

export function deleteApplication(id) {
  return request(`/api/applications/${id}/`, { method: 'DELETE' })
}

export function listVacancies({ q, category, page = 1 } = {}) {
  const params = new URLSearchParams({ page })
  if (q) params.set('q', q)
  if (category) params.set('category', category)
  return request(`/api/vacancies/?${params}`)
}

export function getRates() {
  return request('/api/rates/')
}
