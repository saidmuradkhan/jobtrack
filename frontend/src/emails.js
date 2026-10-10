import { statusLabel } from './statuses.js'

export const GMAIL_FILTER =
  'from:(jobs-noreply@linkedin.com OR greenhouse.io OR greenhouse-mail.io OR lever.co OR ' +
  'myworkdayjobs.com OR ashbyhq.com OR smartrecruiters.com) OR subject:(application OR ' +
  'applying OR interview OR offer OR müraciət OR müsahibə)'

function applicationName(application) {
  return `${application.position} at ${application.company}`
}

export function describeEmail(email) {
  const { application } = email
  switch (email.outcome) {
    case 'created':
      return `Added ${applicationName(application ?? email)}`
    case 'updated':
      return `${applicationName(application ?? email)}: ${statusLabel(email.previous_status)} → ${statusLabel(email.status)}`
    case 'unchanged':
      return application ? `${applicationName(application)}: no change` : 'No change'
    case 'dismissed':
      return 'Dismissed'
    case 'ignored':
      return 'Not about a job, skipped'
    default:
      return 'Waiting for you'
  }
}

export function guessLabel(email) {
  const who = [email.position, email.company].filter(Boolean).join(' at ')
  return `${who || 'Unknown company'} → ${statusLabel(email.status)}`
}
