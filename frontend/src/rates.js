import { useEffect, useState } from 'react'
import { getRates } from './api.js'

let pending = null

/** Official CBAR rates as { USD: 1.7, EUR: 1.9, ... }: the price of one unit in AZN. */
export function useRates() {
  const [rates, setRates] = useState(null)

  useEffect(() => {
    let ignore = false
    pending ??= getRates()
      .then((data) => data.per_unit)
      .catch(() => {
        pending = null
        return null
      })
    pending.then((perUnit) => !ignore && setRates(perUnit))
    return () => {
      ignore = true
    }
  }, [])

  return rates
}

function toAzn(amount, currency, rates) {
  if (currency === 'AZN') return amount
  return rates[currency] ? amount * rates[currency] : null
}

const whole = (amount) => Math.round(amount).toLocaleString('en-US')

/** "≈ $1,176" for AZN, "≈ 5,100 AZN" for USD, both for other currencies. */
export function convertedSalary(amount, currency, rates) {
  if (amount == null || !rates) return ''
  const azn = toAzn(amount, currency, rates)
  if (azn == null) return ''

  const parts = []
  if (currency !== 'AZN') parts.push(`${whole(azn)} AZN`)
  if (currency !== 'USD' && rates.USD) parts.push(`$${whole(azn / rates.USD)}`)
  return parts.length ? `≈ ${parts.join(' · ')}` : ''
}
