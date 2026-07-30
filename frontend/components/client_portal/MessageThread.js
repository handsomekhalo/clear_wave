"use client"

// ─────────────────────────────────────────────────────────────────────────────
// FILE 1: components/client_portal/MessageThread.js
// Wired — fetches messages, sends messages, auto scrolls
// MessageBubble stays exactly as you have it
// ─────────────────────────────────────────────────────────────────────────────

import { useState, useEffect, useRef } from "react"
import { format } from "date-fns"
import { MessageSquare, Send } from "lucide-react"
import backendApi from "../../lib/backendApi"
import { MessageBubble } from "./MessageBubble"

export default function MessageThread({ caseId, initialMessages = [] }) {
    console.log("MessageThread mounted with caseId:", caseId)  // add this

  const [messages, setMessages] = useState(initialMessages)
  const [input, setInput]       = useState("")
  const [sending, setSending]   = useState(false)
  const bottomRef               = useRef(null)

  const token = () => localStorage.getItem("authToken")

  // ── fetch ─────────────────────────────────────────────────────────────────

  const fetchMessages = async () => {
    try {
      const res = await backendApi.get(
        `/client_management/list_case_messages/${caseId}/`,
        { headers: { Authorization: `Token ${token()}` } }
      )
      // unwrap proxy response { status, data: [...] }
      const data = res.data?.data ?? res.data
      console.log("Fetched messages for client :", data)
      setMessages(Array.isArray(data) ? data : [])
    } catch (err) {
      console.error("Failed to load messages", err)
    }
  }

  // useEffect(() => {
  //   fetchMessages()
  // }, [caseId])
    useEffect(() => {
    setMessages(initialMessages)
  }, [initialMessages])

  // ── auto scroll ───────────────────────────────────────────────────────────

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // ── send ──────────────────────────────────────────────────────────────────

  const handleSend = async () => {
    if (!input.trim() || sending) return
    setSending(true)

    try {
      const res = await backendApi.post(
        `/client_management/send_case_message/${caseId}/`,
        { content: input.trim() },
        { headers: { Authorization: `Token ${token()}` } }
      )
      // unwrap and push new message
      const newMessage = res.data?.data ?? res.data
      setMessages(prev => [...prev, newMessage])
      setInput("")
    } catch (err) {
      console.error("Failed to send message", err)
    } finally {
      setSending(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // ── render ────────────────────────────────────────────────────────────────

  return (
    <div className="bg-white rounded-2xl border border-gray-100 flex flex-col">

      {/* Header */}
      <div className="px-5 py-4 border-b border-gray-50">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-gray-400" />
          <h3 className="text-[14px] font-semibold text-gray-900">Messages</h3>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 px-5 py-4 space-y-4 max-h-80 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="text-center py-8">
            <MessageSquare className="w-7 h-7 text-gray-200 mx-auto mb-2" />
            <p className="text-[13px] text-gray-400">No messages yet. Start the conversation.</p>
          </div>
        ) : (
          messages.map((msg, i) => (
            <MessageBubble key={msg.id ?? i} message={msg} />
          ))
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="px-5 pb-5 pt-3 border-t border-gray-50">
        <div className="flex gap-2 items-end">
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message... (Enter to send)"
            rows={2}
            className="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || sending}
            className={`p-2.5 rounded-xl transition ${
              input.trim() && !sending
                ? "bg-blue-600 text-white hover:bg-blue-700"
                : "bg-gray-100 text-gray-400 cursor-not-allowed"
            }`}
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
