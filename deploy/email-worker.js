// Cloudflare Email Worker: catch-all for the inbox domain, hands each email to jobtrack.
// Settings: JOBTRACK_INBOX_URL (https://jobs-api.saidmuradkhan.dev/api/inbox/receive/)
// and the secret INBOX_WEBHOOK_SECRET (same value as on the jobtrack API).
export default {
  async email(message, env) {
    const response = await fetch(env.JOBTRACK_INBOX_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'message/rfc822',
        'X-Inbox-Secret': env.INBOX_WEBHOOK_SECRET,
        'X-Inbox-To': message.to,
      },
      body: await new Response(message.raw).arrayBuffer(),
    })
    if (response.status === 404) {
      message.setReject('Unknown address')
    } else if (!response.ok) {
      throw new Error(`jobtrack answered ${response.status}`)
    }
  },
}
