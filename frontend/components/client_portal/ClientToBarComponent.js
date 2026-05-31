"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { Scale, LogOut } from "lucide-react"

export default function ClientTopBar({ activePage }) {
  const router = useRouter()

  const handleLogout = () => {
    localStorage.removeItem("authToken")
    localStorage.removeItem("user")
    router.push("/client/auth")
  }

  return (
    <header className="bg-white border-b border-gray-100 sticky top-0 z-30">
      <div className="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between">

        {/* Logo */}
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center">
            <Scale className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="text-[14px] font-semibold text-gray-900">
            ClearWave
          </span>
        </div>

        {/* Nav */}
        <nav className="flex items-center gap-1">
          <Link
            href="/client_portal/dashboard"
            className={`px-3 py-1.5 rounded-lg text-[13px] font-medium ${
              activePage === "dashboard"
                ? "bg-blue-50 text-blue-600"
                : "text-gray-500 hover:text-gray-800 hover:bg-gray-50"
            }`}
          >
            My Case
          </Link>

    
          <button
            onClick={handleLogout}
            className="ml-1 p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-50"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </nav>

      </div>
    </header>
  )
}