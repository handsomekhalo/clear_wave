"use client"

import { format } from "date-fns"
import { ArrowRight } from "lucide-react"
import ClientStatusBadge from "./ClientStatusBadgeComponent"


export default function CaseCard({ caseItem, onView }) {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5 hover:border-gray-200 hover:shadow-sm transition-all duration-150">
      
      <div className="flex items-start justify-between gap-3 mb-3">
        <div>
          <h3 className="text-[15px] font-semibold text-gray-900">
            {caseItem.title}
          </h3>

          {caseItem.reference_number && (
            <span className="text-[11.5px] text-gray-400 font-mono block">
              #{caseItem.reference_number}
            </span>
          )}
        </div>

        <ClientStatusBadge status={caseItem.status} />
      </div>

      {caseItem.description && (
        <p className="text-[13px] text-gray-400 mb-4 line-clamp-2">
          {caseItem.description}
        </p>
      )}

      <div className="flex items-center justify-between">
        <span className="text-[12px] text-gray-400">
          {caseItem.updated_at
            ? `Updated ${format(new Date(caseItem.updated_at), "MMM d, yyyy")}`
            : caseItem.created_at
            ? `Created ${format(new Date(caseItem.created_at), "MMM d, yyyy")}`
            : ""}
        </span>

        <button
          onClick={onView}
          className="flex items-center gap-1.5 text-[13px] font-medium text-blue-600 hover:text-blue-700"
        >
          View Case
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

    </div>
  )
}