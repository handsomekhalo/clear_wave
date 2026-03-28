"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"


import ClientTopBar from "../../../components/client_portal/ClientToBarComponent"
import ClientStatusBadge from "../../../components/client_portal/ClientStatusBadgeComponent"
import MessageThread from "../../../components/client_portal/MessageThread"
import { getClientCaseDetail} from "../../../lib/api/client_portal"

export default function ClientCaseDetailPage() {
  const { id } = useParams()

  const [caseData, setCaseData] = useState(null)
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return

    const fetchData = async () => {
      try {
        const caseRes = await getClientCaseDetail(id)

        console.log('case res =========', caseRes)
        const msgRes = await getCaseMessages(id)

        setCaseData(caseRes)
        setMessages(msgRes || [])
      } catch (err) {
        console.error("Error loading case", err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [id])

  if (loading) {
    return (
      <div className="p-6 text-sm text-gray-500">
        Loading case...
      </div>
    )
  }

  if (!caseData) {
    return (
      <div className="p-6 text-sm text-red-500">
        Case not found
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">

      <ClientTopBar activePage="dashboard" />

      <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">

        {/* CASE HEADER */}
        <div className="bg-white rounded-2xl border border-gray-100 p-5">

          <div className="flex justify-between items-start mb-3">
            <div>
              <h1 className="text-lg font-semibold text-gray-900">
                {caseData.title}
              </h1>

              {caseData.reference_number && (
                <p className="text-xs text-gray-400 font-mono mt-1">
                  #{caseData.reference_number}
                </p>
              )}
            </div>

            <ClientStatusBadge status={caseData.status} />
          </div>

          {caseData.description && (
            <p className="text-sm text-gray-500 mt-3">
              {caseData.description}
            </p>
          )}
        </div>

        {/* DOCUMENTS SECTION (placeholder for now) */}
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">
            Documents
          </h3>

          {caseData.documents?.length > 0 ? (
            <div className="space-y-2">
              {caseData.documents.map((doc) => (
                <div
                  key={doc.id}
                  className="text-sm text-blue-600 cursor-pointer"
                >
                  {doc.file_name}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-400">
              No documents available
            </p>
          )}
        </div>

        {/* MESSAGES */}
        <MessageThread caseId={id} initialMessages={messages} />

      </div>
    </div>
  )
}