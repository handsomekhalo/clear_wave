"use client"

// ─────────────────────────────────────────────────────────────────────────────
// FILE 2: app/reset-password/page.js
// Takes token from URL, new password + confirm password
// ─────────────────────────────────────────────────────────────────────────────

import { useState, useEffect } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import backendApi from "../../lib/backendApi"
import Link from "next/link"

export default function ResetPasswordPage() {
  const searchParams= useSearchParams()
  const router= useRouter()
  const token= searchParams.get("token")

  const [newPassword, setNewPassword]         = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showNew, setShowNew]                 = useState(false)
  const [showConfirm, setShowConfirm]         = useState(false)
  const [loading, setLoading]                 = useState(false)
  const [error, setError]                     = useState(null)

  useEffect(() => {
    if (!token) {
      router.replace("/forgot_password")
    }
  }, [token])

  const passwordsMatch = newPassword && confirmPassword && newPassword === confirmPassword
  const isStrong       = newPassword.length >= 8

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    if (!isStrong) {
      setError("Password must be at least 8 characters.")
      return
    }
    if (!passwordsMatch) {
      setError("Passwords do not match.")
      return
    }

    setLoading(true)
    try {
      await backendApi.post(
        "/system_management/confirm_password_reset/",
        {
          token,
          new_password: newPassword,
          confirm_password: confirmPassword,
        }
      )
      router.push("/password_reset/done")
    } catch (err) {
      console.error("Password reset failed", err)
      const msg =
        err?.response?.data?.data?.error ||
        err?.response?.data?.error ||
        "Reset failed. The link may have expired."
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  if (!token) return null

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-sm space-y-6">

        {/* Header */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900">Set new password</h2>
          <p className="text-sm text-gray-500 mt-2">
            Choose a strong password for your account.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 text-sm px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {/* New password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              New Password
            </label>
            <div className="relative">
              <input
                type={showNew ? "text" : "password"}
                required
                value={newPassword}
                onChange={e => setNewPassword(e.target.value)}
                placeholder="At least 8 characters"
                className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 pr-10"
              />
              <button
                type="button"
                onClick={() => setShowNew(p => !p)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 text-xs"
              >
                {showNew ? "Hide" : "Show"}
              </button>
            </div>
            {newPassword && (
              <p className={`text-xs mt-1 ${isStrong ? "text-green-600" : "text-red-500"}`}>
                {isStrong ? "✓ Strong enough" : "Too short — minimum 8 characters"}
              </p>
            )}
          </div>

          {/* Confirm password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Confirm Password
            </label>
            <div className="relative">
              <input
                type={showConfirm ? "text" : "password"}
                required
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                placeholder="Repeat your password"
                className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 pr-10"
              />
              <button
                type="button"
                onClick={() => setShowConfirm(p => !p)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 text-xs"
              >
                {showConfirm ? "Hide" : "Show"}
              </button>
            </div>
            {confirmPassword && (
              <p className={`text-xs mt-1 ${passwordsMatch ? "text-green-600" : "text-red-500"}`}>
                {passwordsMatch ? "✓ Passwords match" : "Passwords do not match"}
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading || !isStrong || !passwordsMatch}
            className={`w-full py-2.5 rounded-lg text-sm font-semibold text-white transition ${
              loading || !isStrong || !passwordsMatch
                ? "bg-gray-300 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700"
            }`}
          >
            {loading ? "Resetting..." : "Reset Password"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500">
          <Link href="/forgot-password" className="text-blue-600 hover:text-blue-700">
            Request a new link
          </Link>
        </p>
      </div>
    </div>
  )
}