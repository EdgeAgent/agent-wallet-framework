"""Provider stubs only. No API calls, no keys, no money movement.
Real funding: user completes checkout in their own Stripe / PayPal / bank / crypto wallet.
Bring your own provider account. Compliance is yours."""
PROVIDERS = {
  "stripe": "Visa / card via Stripe Checkout in your own Stripe account. Agent never sees the card.",
  "paypal": "PayPal checkout in your own PayPal account.",
  "interac": "Interac e-Transfer from your own bank app. No public agent API in Canada.",
  "visa": "Visa via Stripe (see stripe). No direct card handling in this framework.",
  "bitcoin": "BTC from your own wallet to an address you control. No private keys in this framework.",
  "ethereum": "ETH from your own wallet to an address you control. No private keys in this framework.",
}
