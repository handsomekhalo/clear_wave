"use client"

import { useState, useEffect } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import backendApi from "../../../lib/backendApi"

console.log("AUTH PAGE LOADED")  // confirm page loads
export default function ClientAuthPage() {
  const [email, setEmail] = useState("")
  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(false)

  const searchParams = useSearchParams()
  const router = useRouter()

  const token = searchParams.get("token")
  console.log("AUTH PAGE TOKEN:", token)  // confirm we get the token from URL
  // 🔐 AUTO LOGIN WITH TOKEN
 useEffect(() => {
  if (!token) return

  const loginWithToken = async () => {
    setLoading(true)

    try {
      const res = await backendApi.post(
        "/client_management/sign_in_with_link/",
        { token }
      )
      console.log("FULL RES:", res)
        console.log("RES.DATA:", res.data)
        console.log("RES.DATA.DATA:", res.data?.data)  // check if data is nested under 'data' key
          // unwrap proxy response
      const data = res.data?.data ?? res.data
      const authToken = data.token
      const user = data.user

      // const authToken = res.data.token
      console.log("TOKEN:", authToken)  // confirm it's not null
      // const user = res.data.user

      localStorage.setItem("authToken", authToken)
      localStorage.setItem("user", JSON.stringify(user))

      router.replace("/client_portal/dashboard")

    } catch (err) {
      console.error(err)
      setMessage("Invalid or expired link.")
    } finally {
      setLoading(false)
    }
  }

  loginWithToken()
}, [token])
  // 📩 REQUEST MAGIC LINK
  const handleRequestLink = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage("")

    try {
      await backendApi.post(
        "/client_management/request_magic_link/",
        { email }
      )

      setMessage("If your email exists, a login link has been sent.")

    } catch (err) {
      console.error(err)
      setMessage("Something went wrong.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-6">
      <div className="w-full max-w-sm space-y-6">

        <h2 className="text-2xl font-bold text-center">
          Client Portal Access
        </h2>

        {/* If no token → show email form */}
        {!token && (
          <form onSubmit={handleRequestLink} className="space-y-4">

            <input
              type="email"
              required
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border p-2 rounded"
            />

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-black text-white p-2 rounded"
            >
              {loading ? "Sending..." : "Login"}
            </button>

          </form>
        )}

        {/* Feedback */}
        {message && (
          <p className="text-sm text-center text-gray-600">
            {message}
          </p>
        )}

      </div>
    </div>
  )
}