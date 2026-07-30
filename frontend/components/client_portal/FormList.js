"use client"

// ─────────────────────────────────────────────────────────────────────────────
// FILE: components/client_portal/FormsList.js
// ─────────────────────────────────────────────────────────────────────────────

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import  {getClientFormAssignments} from "../../lib/api/client_portal"

import {
  CheckCircle,
  XCircle,
  ArrowRight,
} from "lucide-react"



const STATUS_STYLES = {
  pending: {
    bg: "bg-gray-100 text-gray-600",
    icon: null,
  },

  in_progress: {
    bg: "bg-blue-100 text-blue-700",
    icon: null,
  },

  submitted: {
    bg: "bg-yellow-100 text-yellow-700",
    icon: null,
  },

  under_review: {
    bg: "bg-orange-100 text-orange-700",
    icon: null,
  },

  approved: {
    bg: "bg-green-100 text-green-700",
    icon: CheckCircle,
  },

  rejected: {
    bg: "bg-red-100 text-red-700",
    icon: XCircle,
  },
}

export default function FormsList() {
  const [assignments, setAssignments] = useState([])
  const [loading, setLoading] = useState(true)

  const router = useRouter()


// replace the entire useEffect with this:
useEffect(() => {
  const fetchAssignments = async () => {
    try {
      const res = await getClientFormAssignments()
      console.log("Form assignments raw response:", res)
      const data = res.data ?? res
      console.log("Form assignments unwrapped data:", data)
      setAssignments(Array.isArray(data) ? data : [])
    } catch (err) {
      console.error("Failed to load forms", err)
    } finally {
      setLoading(false)
    }
  }

  fetchAssignments()
}, [])

  if (loading) {
    return (
      <div className="text-sm text-gray-400 py-6 text-center">
        Loading forms...
      </div>
    )
  }

  if (assignments.length === 0) {
    return null
  }

  return (
    <div className="space-y-3">

      <h2 className="text-[15px] font-semibold text-gray-900">
        Forms to Complete
      </h2>

      {assignments.map((a) => {
        const style =
          STATUS_STYLES[a.status] ??
          STATUS_STYLES.pending

        const isOverdue = a.is_overdue

        const canEdit = [
          "pending",
          "in_progress",
          "rejected",
        ].includes(a.status)

        const isSubmitted = [
          "submitted",
          "approved",
          "under_review",
        ].includes(a.status)

        return (
          <div
            key={a.id}
            className="bg-white rounded-2xl border border-gray-100 p-5 hover:border-gray-200 hover:shadow-sm transition-all duration-150"
          >

            <div className="flex items-start justify-between gap-3">

              <div className="space-y-1">

                <p className="text-[15px] font-semibold text-gray-900">
                  {a.template?.name}
                </p>

                <p className="text-[12px] text-gray-400 font-mono">
                  {a.case_reference ??
                    a.case?.reference_number}
                </p>

                {/* status pill */}
                <span
                  className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${style.bg}`}
                >
                  {style.icon && (
                    <style.icon className="h-3 w-3" />
                  )}

                  {a.status_display ?? a.status}
                </span>

                {/* due date */}
                {a.due_date && (
                  <p
                    className={`text-[12px] ${
                      isOverdue
                        ? "text-red-600 font-medium"
                        : "text-gray-400"
                    }`}
                  >
                    {isOverdue
                      ? "⚠️ Overdue · "
                      : "Due · "}

                    {new Date(a.due_date).toLocaleDateString(
                      "en-ZA",
                      {
                        day: "numeric",
                        month: "short",
                        year: "numeric",
                      }
                    )}
                  </p>
                )}

                {/* rejection notes */}
                {a.status === "rejected" &&
                  a.review_notes && (
                    <div className="mt-2 rounded-lg bg-red-50 border border-red-100 px-3 py-2">

                      <p className="text-xs font-medium text-red-700 mb-0.5">
                        Returned for corrections
                      </p>

                      <p className="text-xs text-red-600">
                        {a.review_notes}
                      </p>
                    </div>
                  )}
              </div>

              {/* CTA */}
              <div className="flex-shrink-0">

                {canEdit && (
                  <button
                    onClick={() =>
                      router.push(
                        `/client_portal/forms/${a.id}`
                      )
                    }
                    className="flex items-center gap-1.5 text-[13px] font-medium text-blue-600 hover:text-blue-700"
                  >
                    {a.status === "rejected"
                      ? "Edit & Resubmit"
                      : "Complete Form"}

                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                )}

                {isSubmitted && (
                  <button
                    onClick={() =>
                      router.push(
                        `/client_portal/forms/${a.id}/view`
                      )
                    }
                    className="flex items-center gap-1.5 text-[13px] font-medium text-gray-500 hover:text-gray-700"
                  >
                    View Submission

                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}