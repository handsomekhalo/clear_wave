"use client"

import { X, Download } from "lucide-react"

export default function DocumentViewerModal({ doc, onClose }) {
  console.log("IFRAME URL:", doc?.url)
  if (!doc) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">

      <div className="bg-white rounded-2xl shadow-xl w-full max-w-3xl flex flex-col max-h-[90vh]">

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <div>
            <h3 className="text-[14px] font-semibold text-gray-900">
              {doc.file_name}
            </h3>

            {doc.description && (
              <p className="text-[12px] text-gray-400 mt-0.5">
                {doc.description}
              </p>
            )}
          </div>

          <div className="flex items-center gap-2">
            <a
              href={doc.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12.5px] font-medium text-blue-600 hover:bg-blue-50 border border-blue-100"
            >
              <Download className="w-3.5 h-3.5" />
              Download
            </a>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-50"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Viewer */}
        <div className="flex-1 overflow-hidden rounded-b-2xl">
          <iframe
            src={doc.url}
            className="w-full h-full min-h-[500px]"
            title={doc.file_name}
          />
        </div>

      </div>
    </div>
  )
}