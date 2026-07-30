"use client"

// ─────────────────────────────────────────────────────────────────────────────
// FILE 3: app/reset-password/done/page.js
// Confirmation screen after successful reset
// ─────────────────────────────────────────────────────────────────────────────

import Link from "next/link"

export default function ResetPasswordDonePage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-sm space-y-6 text-center">

        {/* Success icon */}
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
          <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>

        <div>
          <h2 className="text-2xl font-bold text-gray-900">Password reset</h2>
          <p className="text-sm text-gray-500 mt-2">
            Your password has been updated successfully.
            All previous sessions have been logged out.
          </p>
        </div>

        <Link
          href="/login"
          className="block w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg text-center transition"
        >
          Back to Login
        </Link>

      </div>
    </div>
  )
}