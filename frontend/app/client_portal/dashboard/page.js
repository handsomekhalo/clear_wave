"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import backendApi from "@/utils/backendApi"

import ClientTopBar from "../../../components/client_portal/ClientToBarComponent"
import CaseCard from "../../../components/client_portal/CaseCardComponent"
import { getClientCaseDetail } from "../../../lib/api/client_portal"
import { getClientCases } from "../../../lib/api/client_portal"

export default function ClientDashboard() {
  const [cases, setCases] = useState([])
  const [loading, setLoading] = useState(true)

  const router = useRouter()
  

  const fetchCases = async () => {
    try {
      // const data = await getClientCases()
      const data = await getClientCases()
      console.log("CASES RAW:", data)
      setCases(data.data || [])
    } catch (err) {
      console.error("Failed to load cases", err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCases()
  }, [])

  const handleViewCase = (caseId) => {
  router.push(`/client_portal/client_cases/${caseId}`)
}
  // const handleViewCase = (caseId) => {
  //   router.push(`/client_portal/client_cases/${caseId}`)
  // }

  return (
    <div className="min-h-screen bg-gray-50">

      <ClientTopBar activePage="dashboard" />

      <div className="max-w-4xl mx-auto px-4 py-6">

        <h1 className="text-xl font-semibold text-gray-900 mb-6">
          My Cases
        </h1>

        {loading ? (
          <p className="text-sm text-gray-500">Loading cases...</p>
        ) : cases.length === 0 ? (
          <div className="text-center text-sm text-gray-500 py-10 border rounded-lg">
            No cases assigned yet
          </div>
        ) : (
          <div className="grid gap-4">
            {cases.map((c) => (
  c && (
    <CaseCard
      key={c.id}
      caseItem={c}
      onView={() => handleViewCase(c.id)}
    />
  )
))}
            {/* {cases.map((c) => (
              <CaseCard
                key={c.id}
                case={c}  
                onView={() => handleViewCase(c.id)}
              />
            ))} */}
          </div>
        )}

      </div>
    </div>
  )
}