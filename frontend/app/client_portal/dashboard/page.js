"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { getClientCases } from "../../../lib/api/client_portal"
import { getClientFormAssignments } from "../../../lib/api/client_portal"
import ClientTopBar from "../../../components/client_portal/ClientToBarComponent"
import { format } from "date-fns"
import {
  ArrowRight, FileText, MessageSquare, Clock,
  CheckCircle, XCircle, AlertCircle, ClipboardList,
  ChevronRight, Folder
} from "lucide-react"

// ── Status config ────────────────────────────────────────────────────────────

const CASE_STATUS = {
  new:       { label: "New",       dot: "bg-sky-400",    text: "text-sky-700",    bg: "bg-sky-50"    },
  active:    { label: "Active",    dot: "bg-emerald-400",text: "text-emerald-700",bg: "bg-emerald-50"},
  on_hold:   { label: "On Hold",   dot: "bg-amber-400",  text: "text-amber-700",  bg: "bg-amber-50"  },
  closed:    { label: "Closed",    dot: "bg-slate-400",  text: "text-slate-600",  bg: "bg-slate-50"  },
  archived:  { label: "Archived",  dot: "bg-slate-300",  text: "text-slate-500",  bg: "bg-slate-50"  },
}

const FORM_STATUS = {
  pending:      { label: "Not Started",   bg: "bg-slate-100",   text: "text-slate-600",   icon: ClipboardList },
  in_progress:  { label: "In Progress",   bg: "bg-blue-100",    text: "text-blue-700",    icon: Clock         },
  submitted:    { label: "Submitted",     bg: "bg-violet-100",  text: "text-violet-700",  icon: CheckCircle   },
  under_review: { label: "Under Review",  bg: "bg-amber-100",   text: "text-amber-700",   icon: Clock         },
  approved:     { label: "Approved",      bg: "bg-emerald-100", text: "text-emerald-700", icon: CheckCircle   },
  rejected:     { label: "Needs Changes", bg: "bg-red-100",     text: "text-red-700",     icon: XCircle       },
}

function StatusPill({ status, map }) {
  const s = map[status] ?? { label: status, bg: "bg-slate-100", text: "text-slate-600", dot: "bg-slate-400" }
  const Icon = s.icon
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full ${s.bg} ${s.text}`}>
      {s.dot && <span className={`w-1.5 h-1.5 rounded-full ${s.dot}`} />}
      {Icon && <Icon className="w-3 h-3" />}
      {s.label}
    </span>
  )
}

// ── Action-required form banner ───────────────────────────────────────────────

function ActionBanner({ forms, onGo }) {
  const actionable = forms.filter(f => ["pending","in_progress","rejected"].includes(f.status))
  if (actionable.length === 0) return null

  return (
    <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 space-y-2">
      <div className="flex items-center gap-2 mb-1">
        <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
        <p className="text-sm font-semibold text-amber-800">
          {actionable.length === 1
            ? "1 form needs your attention"
            : `${actionable.length} forms need your attention`}
        </p>
      </div>
      {actionable.map(f => (
        <div
          key={f.id}
          onClick={() => onGo(f)}
          className="flex items-center justify-between bg-white rounded-xl px-4 py-3 border border-amber-100 cursor-pointer hover:border-amber-300 hover:shadow-sm transition-all group"
        >
          <div className="min-w-0">
            <p className="text-sm font-medium text-slate-800 truncate">{f.template?.name}</p>
            <p className="text-xs text-slate-400 font-mono">{f.case_reference ?? f.case?.reference_number}</p>
            {f.status === "rejected" && f.review_notes && (
              <p className="text-xs text-red-600 mt-0.5 truncate">↩ {f.review_notes}</p>
            )}
          </div>
          <div className="flex items-center gap-2 ml-3 shrink-0">
            <StatusPill status={f.status} map={FORM_STATUS} />
            <ChevronRight className="w-4 h-4 text-amber-500 group-hover:translate-x-0.5 transition-transform" />
          </div>
        </div>
      ))}
    </div>
  )
}

// ── Case card ─────────────────────────────────────────────────────────────────

function CaseCard({ c, pendingForms, onView }) {
  const s = CASE_STATUS[c.status] ?? CASE_STATUS.active
  const formCount = pendingForms.filter(f =>
    (f.case_reference === c.reference_number || f.case === c.id) &&
    ["pending","in_progress","rejected"].includes(f.status)
  ).length

  return (
    <div
      onClick={onView}
      className="group bg-white rounded-2xl border border-slate-100 p-5 cursor-pointer hover:border-slate-200 hover:shadow-md transition-all duration-200"
    >
      {/* Top row */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="min-w-0">
          <h3 className="text-[15px] font-semibold text-slate-900 truncate">{c.title}</h3>
          {c.reference_number && (
            <span className="text-[11px] text-slate-400 font-mono">{c.reference_number}</span>
          )}
        </div>
        <StatusPill status={c.status} map={CASE_STATUS} />
      </div>

      {/* Description */}
      {c.description && (
        <p className="text-[13px] text-slate-500 line-clamp-2 mb-4">{c.description}</p>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-slate-50">
        <div className="flex items-center gap-3 text-[12px] text-slate-400">
          {/* Pending forms badge */}
          {formCount > 0 && (
            <span className="flex items-center gap-1 text-amber-600 font-medium">
              <FileText className="w-3.5 h-3.5" />
              {formCount} form{formCount > 1 ? "s" : ""} pending
            </span>
          )}
          {/* Updated */}
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {c.updated_at
              ? format(new Date(c.updated_at), "d MMM yyyy")
              : c.created_at
              ? format(new Date(c.created_at), "d MMM yyyy")
              : ""}
          </span>
        </div>
        <span className="flex items-center gap-1 text-[13px] font-medium text-blue-600 group-hover:gap-2 transition-all">
          View
          <ArrowRight className="w-3.5 h-3.5" />
        </span>
      </div>
    </div>
  )
}

// ── Skeleton ──────────────────────────────────────────────────────────────────

function Skeleton() {
  return (
    <div className="space-y-6">
      <div className="rounded-2xl bg-slate-100 animate-pulse h-24" />
      <div className="space-y-3">
        {[1,2].map(i => (
          <div key={i} className="rounded-2xl bg-slate-100 animate-pulse h-32" />
        ))}
      </div>
    </div>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function ClientDashboard() {
  const [cases, setCases]         = useState([])
  const [forms, setForms]         = useState([])
  const [loading, setLoading]     = useState(true)
  const router = useRouter()

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [casesRes, formsRes] = await Promise.all([
          getClientCases(),
          getClientFormAssignments(),
        ])
        setCases(Array.isArray(casesRes) ? casesRes : [])
        const fd = formsRes?.data ?? formsRes
        setForms(Array.isArray(fd) ? fd : [])
      } catch (err) {
        console.error("Dashboard load failed", err)
      } finally {
        setLoading(false)
      }
    }
    fetchAll()
  }, [])

  const handleFormGo = (f) => {
    if (["pending","in_progress","rejected"].includes(f.status)) {
      router.push(`/client_portal/forms/${f.id}`)
    } else {
      router.push(`/client_portal/forms/${f.id}/view`)
    }
  }

  // Submitted/approved forms for the "All Forms" section
  const completedForms = forms.filter(f =>
    ["submitted","under_review","approved"].includes(f.status)
  )

  return (
    <div className="min-h-screen bg-slate-50">
      <ClientTopBar activePage="dashboard" />

      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">

        {loading ? (
          <Skeleton />
        ) : (
          <>
            {/* ── Action required banner ─────────────────────── */}
            <ActionBanner forms={forms} onGo={handleFormGo} />

            {/* ── My Cases ───────────────────────────────────── */}
            <section>
              <div className="flex items-center gap-2 mb-3">
                <Folder className="w-4 h-4 text-slate-400" />
                <h2 className="text-[15px] font-semibold text-slate-800">My Cases</h2>
                {cases.length > 0 && (
                  <span className="ml-auto text-xs text-slate-400">{cases.length} case{cases.length !== 1 ? "s" : ""}</span>
                )}
              </div>

              {cases.length === 0 ? (
                <div className="bg-white rounded-2xl border border-slate-100 p-10 text-center">
                  <Folder className="w-8 h-8 text-slate-200 mx-auto mb-2" />
                  <p className="text-sm text-slate-400">No cases assigned yet</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {cases.map(c => c && (
                    <CaseCard
                      key={c.id}
                      c={c}
                      pendingForms={forms}
                      onView={() => router.push(`/client_portal/client_cases/${c.id}`)}
                    />
                  ))}
                </div>
              )}
            </section>

            {/* ── Completed / submitted forms ─────────────────── */}
            {completedForms.length > 0 && (
              <section>
                <div className="flex items-center gap-2 mb-3">
                  <ClipboardList className="w-4 h-4 text-slate-400" />
                  <h2 className="text-[15px] font-semibold text-slate-800">Submitted Forms</h2>
                </div>
                <div className="space-y-2">
                  {completedForms.map(f => (
                    <div
                      key={f.id}
                      onClick={() => router.push(`/client_portal/forms/${f.id}/view`)}
                      className="flex items-center justify-between bg-white rounded-xl border border-slate-100 px-4 py-3 cursor-pointer hover:border-slate-200 hover:shadow-sm transition-all group"
                    >
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-slate-800 truncate">{f.template?.name}</p>
                        <p className="text-xs text-slate-400 font-mono">{f.case_reference ?? f.case?.reference_number}</p>
                      </div>
                      <div className="flex items-center gap-2 ml-3 shrink-0">
                        <StatusPill status={f.status} map={FORM_STATUS} />
                        <ChevronRight className="w-4 h-4 text-slate-300 group-hover:translate-x-0.5 transition-transform" />
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </>
        )}
      </div>
    </div>
  )
}

// "use client"

// import { useEffect, useState } from "react"
// import { useRouter } from "next/navigation"

// import ClientTopBar from "../../../components/client_portal/ClientToBarComponent"
// import CaseCard from "../../../components/client_portal/CaseCardComponent"
// import { getClientCases } from "../../../lib/api/client_portal"
// import FormsList from "../../../components/client_portal/FormList"

// export default function ClientDashboard() {
//   const [cases, setCases] = useState([])
//   const [loading, setLoading] = useState(true)
//   const router = useRouter()

//   // const fetchCases = async () => {
//   //   try {
//   //     const data = await getClientCases()
//   //     setCases(data.data || [])
//   //     console.log("client dashboard:", data)
//   //   } catch (err) {
//   //     console.error("Failed to load cases", err)
//   //   } finally {
//   //     setLoading(false)
//   //   }
//   // }
// const fetchCases = async () => {
//   try {
//     const data = await getClientCases()
//     console.log("client dashboard:", data)
//     setCases(Array.isArray(data) ? data : [])  // fix this
//   } catch (err) {
//     console.error("Failed to load cases", err)
//   } finally {
//     setLoading(false)
//   }
// }
//   useEffect(() => {
//     fetchCases()
//   }, [])

//   const handleViewCase = (caseId) => {
//     router.push(`/client_portal/client_cases/${caseId}`)
//   }

//   return (
//     <div className="min-h-screen bg-gray-50">

//       <ClientTopBar activePage="dashboard" />

//       <div className="max-w-4xl mx-auto px-4 py-6 space-y-8">

//         {/* MY CASES */}
//         <div>
//           <h1 className="text-xl font-semibold text-gray-900 mb-4">
//             My Cases
//           </h1>

//           {loading ? (
//             <p className="text-sm text-gray-500">Loading cases...</p>
//           ) : cases.length === 0 ? (
//             <div className="text-center text-sm text-gray-500 py-10 border rounded-lg">
//             </div>
//           ) : (
//             <div className="grid gap-4">
//               {cases.map((c) =>
//                 c && (
//                   <CaseCard
//                     key={c.id}
//                     caseItem={c}
//                     onView={() => handleViewCase(c.id)}
//                   />
//                 )
//               )}
//             </div>
//           )}
//         </div>

//         {/* FORMS TO COMPLETE */}
//         <FormsList />

//       </div>
//     </div>
//   )
// }
