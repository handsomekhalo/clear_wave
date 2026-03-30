"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"

import ClientTopBar from "../../../../components/client_portal/ClientToBarComponent"
import ClientStatusBadge from "../../../../components/client_portal/ClientStatusBadgeComponent"
import MessageThread from "../../../../components/client_portal/MessageThread"
import { getClientCaseDetail } from "../../../../lib/api/client_portal"
import { getCaseMessages } from "../../../../lib/api/client_portal"
import { getClientDocuments } from "../../../../lib/api/client_portal"
import DocumentList from "../../../../components/client_portal/DocumentListComponent"

export default function ClientCaseDetailPage() {
  const { id } = useParams()

  const [caseData, setCaseData] = useState(null)
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(true)
  const [documents, setDocuments] = useState([])

  useEffect(() => {
    if (!id) return

const fetchData = async () => {
  try {
    const caseRes = await getClientCaseDetail(id)
    const msgRes = await getCaseMessages(id)
    const docsRes = await getClientDocuments(id)

    console.log("DOCS RESPONSE:", docsRes)

    setCaseData(caseRes)
    setMessages(msgRes || [])
    setDocuments(docsRes?.data || [])
  } catch (err) {
    console.error("Error loading case", err)
  } finally {
    setLoading(false)
  }
}

    fetchData()
  }, [id])

  if (loading) {
    return <div className="p-6 text-gray-500 text-sm">Loading case...</div>
  }

  if (!caseData) {
    return <div className="p-6 text-red-500 text-sm">Case not found</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">

      <ClientTopBar activePage="dashboard" />

      <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">

        {/* CASE HEADER */}
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <div className="flex justify-between items-start">
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

        {/* DOCUMENTS */}
        {/* DOCUMENTS */}
          <div className="bg-white rounded-2xl border border-gray-100 p-5">
  <h3 className="text-sm font-semibold text-gray-900 mb-3">
    Documents
  </h3>

  {documents.length > 0 ? (
    <DocumentList
      caseId={id}
      documents={documents}
    />
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