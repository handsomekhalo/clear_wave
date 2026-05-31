    "use client"

import { useState } from "react"
import backendApi from "../../lib/backendApi"
import DocumentViewerModal from "./DocumentViewerModal"
import { viewDocument } from "../../lib/api/client_portal"

export default function DocumentList({ caseId, documents }) {
  const [viewerOpen, setViewerOpen] = useState(false)
  const [currentDoc, setCurrentDoc] = useState(null)



const handleView = async (doc) => {
  try {
    const res = await viewDocument(doc.id)

    console.log("VIEW RESPONSE:", res)
console.log("VIEW URL:", res?.url)

    setCurrentDoc({
      ...doc,
      url: res.url   // 🔥 from backend
    })

    setViewerOpen(true)

  } catch (err) {
    console.error("Failed to load document", err)
  }
}

  if (!documents || documents.length === 0) {
    return (
      <div className="text-sm text-gray-500 border rounded-lg p-6 text-center">
        No documents available
      </div>
    )
  }

  return (
    <>
      <div className="space-y-3">

        {documents.map((doc) => (
          <div
            key={doc.id}
            className="flex items-center justify-between p-4 border rounded-xl hover:bg-gray-50"
          >
            <div>
              <p className="text-sm font-medium text-gray-900">
                {doc.file_name}
              </p>
              <p className="text-xs text-gray-400">
                {doc.description || "No description"}
              </p>
            </div>

            <button
              onClick={() => handleView(doc)}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              View
            </button>
          </div>
        ))}

      </div>

      {/* Modal */}
      {viewerOpen && (
        <DocumentViewerModal
          doc={currentDoc}
          onClose={() => setViewerOpen(false)}
        />
      )}
    </>
  )
}