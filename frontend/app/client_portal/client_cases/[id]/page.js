"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import ClientTopBar from "../../../../components/client_portal/ClientToBarComponent"
import MessageThread from "../../../../components/client_portal/MessageThread"
import DocumentList from "../../../../components/client_portal/DocumentListComponent"
import { getClientCaseDetail, getCaseMessages, getClientDocuments } from "../../../../lib/api/client_portal"
import {
  ArrowLeft, FileText, MessageSquare, Info,
  Clock, ChevronRight, Calendar
} from "lucide-react"
import { format } from "date-fns"

// ── Status config ─────────────────────────────────────────────────────────────

const CASE_STATUS = {
  new:      { label: "New",      dot: "bg-sky-400",     text: "text-sky-700",    bg: "bg-sky-50"     },
  active:   { label: "Active",   dot: "bg-emerald-400", text: "text-emerald-700",bg: "bg-emerald-50" },
  on_hold:  { label: "On Hold",  dot: "bg-amber-400",   text: "text-amber-700",  bg: "bg-amber-50"   },
  closed:   { label: "Closed",   dot: "bg-slate-400",   text: "text-slate-600",  bg: "bg-slate-50"   },
  archived: { label: "Archived", dot: "bg-slate-300",   text: "text-slate-500",  bg: "bg-slate-50"   },
}

function StatusPill({ status }) {
  const s = CASE_STATUS[status] ?? CASE_STATUS.active
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full ${s.bg} ${s.text}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${s.dot}`} />
      {s.label}
    </span>
  )
}

// ── Tab button ────────────────────────────────────────────────────────────────

function Tab({ id, label, icon: Icon, active, count, onClick }) {
  return (
    <button
      onClick={() => onClick(id)}
      className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
        active
          ? "border-blue-600 text-blue-600"
          : "border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-200"
      }`}
    >
      <Icon className="w-4 h-4" />
      {label}
      {count != null && count > 0 && (
        <span className={`text-xs px-1.5 py-0.5 rounded-full font-semibold ${
          active ? "bg-blue-100 text-blue-700" : "bg-slate-100 text-slate-500"
        }`}>
          {count}
        </span>
      )}
    </button>
  )
}

// ── Skeleton ──────────────────────────────────────────────────────────────────

function Skeleton() {
  return (
    <div className="space-y-4 animate-pulse">
      <div className="h-28 bg-slate-100 rounded-2xl" />
      <div className="h-10 bg-slate-100 rounded-xl" />
      <div className="h-48 bg-slate-100 rounded-2xl" />
    </div>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function ClientCaseDetailPage() {
  const { id } = useParams()
  const router = useRouter()
  const [caseData,  setCaseData]  = useState(null)
  const [messages,  setMessages]  = useState([])
  const [documents, setDocuments] = useState([])
  const [loading,   setLoading]   = useState(true)
  const [activeTab, setActiveTab] = useState("overview")

  useEffect(() => {
    if (!id) return
    const fetchData = async () => {
      try {
        const [caseRes, msgRes, docsRes] = await Promise.all([
          getClientCaseDetail(id),
          getCaseMessages(id),
          getClientDocuments(id),
        ])
        setCaseData(caseRes)
        setMessages(Array.isArray(msgRes) ? msgRes : [])
        setDocuments(docsRes?.data ?? docsRes ?? [])
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
      <div className="min-h-screen bg-slate-50">
        <ClientTopBar activePage="dashboard" />
        <div className="max-w-2xl mx-auto px-4 py-6">
          <Skeleton />
        </div>
      </div>
    )
  }

  if (!caseData) {
    return (
      <div className="min-h-screen bg-slate-50">
        <ClientTopBar activePage="dashboard" />
        <div className="max-w-2xl mx-auto px-4 py-16 text-center">
          <p className="text-sm text-red-500">Case not found.</p>
          <button onClick={() => router.push("/client_portal/dashboard")} className="mt-4 text-sm text-blue-600 hover:underline">
            Back to dashboard
          </button>
        </div>
      </div>
    )
  }

  const unreadMessages = messages.filter(m => !m.is_read && m.sender_type !== "client").length

  return (
    <div className="min-h-screen bg-slate-50">
      <ClientTopBar activePage="dashboard" />

      <div className="max-w-2xl mx-auto px-4 py-6 space-y-4">

        {/* Back */}
        <button
          onClick={() => router.push("/client_portal/dashboard")}
          className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Dashboard
        </button>

        {/* Case header card */}
        <div className="bg-white rounded-2xl border border-slate-100 p-5">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <h1 className="text-lg font-semibold text-slate-900 leading-snug">
                {caseData.title}
              </h1>
              {caseData.reference_number && (
                <p className="text-xs text-slate-400 font-mono mt-0.5">
                  {caseData.reference_number}
                </p>
              )}
            </div>
            <StatusPill status={caseData.status} />
          </div>

          {caseData.description && (
            <p className="text-sm text-slate-500 mt-3 leading-relaxed">
              {caseData.description}
            </p>
          )}

          {/* Meta row */}
          <div className="flex flex-wrap gap-4 mt-4 pt-4 border-t border-slate-50 text-xs text-slate-400">
            {caseData.deadline && (
              <span className="flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5" />
                Deadline {format(new Date(caseData.deadline), "d MMM yyyy")}
              </span>
            )}
            {caseData.matter_type && (
              <span className="flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5" />
                {caseData.matter_type}
              </span>
            )}
            {caseData.updated_at && (
              <span className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5" />
                Updated {format(new Date(caseData.updated_at), "d MMM yyyy")}
              </span>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-2xl border border-slate-100 overflow-hidden">
          {/* Tab bar */}
          <div className="flex border-b border-slate-100 overflow-x-auto">
            <Tab id="overview"   label="Overview"   icon={Info}          active={activeTab === "overview"}   onClick={setActiveTab} />
            <Tab id="documents"  label="Documents"  icon={FileText}      active={activeTab === "documents"}  count={documents.length} onClick={setActiveTab} />
            <Tab id="messages"   label="Messages"   icon={MessageSquare} active={activeTab === "messages"}   count={unreadMessages}   onClick={setActiveTab} />
          </div>

          {/* Tab content */}
          <div className="p-5">

            {/* ── Overview ── */}
            {activeTab === "overview" && (
              <div className="space-y-4">
                {/* Quick stats */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-slate-50 rounded-xl p-4">
                    <p className="text-xs text-slate-400 mb-1">Documents</p>
                    <p className="text-2xl font-bold text-slate-800">{documents.length}</p>
                  </div>
                  <div className="bg-slate-50 rounded-xl p-4">
                    <p className="text-xs text-slate-400 mb-1">Messages</p>
                    <p className="text-2xl font-bold text-slate-800">{messages.length}</p>
                    {unreadMessages > 0 && (
                      <p className="text-xs text-blue-600 font-medium mt-0.5">{unreadMessages} unread</p>
                    )}
                  </div>
                </div>

                {/* Quick links */}
                <div className="space-y-2">
                  <button
                    onClick={() => setActiveTab("documents")}
                    className="w-full flex items-center justify-between px-4 py-3 rounded-xl border border-slate-100 hover:border-slate-200 hover:bg-slate-50 transition-all group text-left"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center">
                        <FileText className="w-4 h-4 text-blue-600" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-slate-800">View Documents</p>
                        <p className="text-xs text-slate-400">{documents.length} file{documents.length !== 1 ? "s" : ""} shared</p>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-slate-300 group-hover:translate-x-0.5 transition-transform" />
                  </button>

                  <button
                    onClick={() => setActiveTab("messages")}
                    className="w-full flex items-center justify-between px-4 py-3 rounded-xl border border-slate-100 hover:border-slate-200 hover:bg-slate-50 transition-all group text-left"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center">
                        <MessageSquare className="w-4 h-4 text-emerald-600" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-slate-800">Messages</p>
                        <p className="text-xs text-slate-400">
                          {unreadMessages > 0
                            ? `${unreadMessages} unread message${unreadMessages !== 1 ? "s" : ""}`
                            : `${messages.length} message${messages.length !== 1 ? "s" : ""}`}
                        </p>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-slate-300 group-hover:translate-x-0.5 transition-transform" />
                  </button>
                </div>
              </div>
            )}

            {/* ── Documents ── */}
            {activeTab === "documents" && (
              <div>
                {documents.length === 0 ? (
                  <div className="py-12 text-center">
                    <FileText className="w-8 h-8 text-slate-200 mx-auto mb-2" />
                    <p className="text-sm text-slate-400">No documents yet</p>
                    <p className="text-xs text-slate-300 mt-1">Your lawyer will share documents here</p>
                  </div>
                ) : (
                  <DocumentList caseId={id} documents={documents} />
                )}
              </div>
            )}

            {/* ── Messages ── */}
            {activeTab === "messages" && (
              <MessageThread caseId={id} initialMessages={messages} />
            )}

          </div>
        </div>

      </div>
    </div>
  )
}

