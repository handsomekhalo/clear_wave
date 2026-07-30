"use client"

// ─────────────────────────────────────────────────────────────────────────────
// FILE 1: app/forgot-password/page.js
// User enters email, clicks send, sees confirmation message
// ─────────────────────────────────────────────────────────────────────────────

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import backendApi from "../../lib/backendApi"

export default function ForgotPasswordPage() {
  const [email, setEmail]     = useState("")
  const [loading, setLoading] = useState(false)
  const [sent, setSent]       = useState(false)
  const [error, setError]     = useState(null)
  const router                = useRouter()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email.trim()) return

    setLoading(true)
    setError(null)

    try {
      await backendApi.post(
        "/system_management/request_password_reset/",
        { email: email.trim().toLowerCase() }
      )
      setSent(true)
    } catch (err) {
      console.error("Password reset request failed", err)
      setError("Something went wrong. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  if (sent) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
        <div className="w-full max-w-sm space-y-6 text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Check your email</h2>
            <p className="text-sm text-gray-500 mt-2">
              If <span className="font-medium text-gray-700">{email}</span> exists
              in our system, a reset link has been sent.
            </p>
            <p className="text-xs text-gray-400 mt-2">
              The link expires in 1 hour. Check your spam folder if you don't see it.
            </p>
          </div>
          <Link
            href="/login"
            className="block text-sm text-blue-600 hover:text-blue-700"
          >
            Back to login
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-sm space-y-6">

        {/* Header */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900">Forgot password?</h2>
          <p className="text-sm text-gray-500 mt-2">
            Enter your email and will send you a reset link.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 text-sm px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading || !email.trim()}
            className={`w-full py-2.5 rounded-lg text-sm font-semibold text-white transition ${
              loading || !email.trim()
                ? "bg-gray-300 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700"
            }`}
          >
            {loading ? "Sending..." : "Send Reset Link"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500">
          Remember your password?{" "}
          <Link href="/login" className="text-blue-600 hover:text-blue-700 font-medium">
            Back to login
          </Link>
        </p>
      </div>
    </div>
  )
}