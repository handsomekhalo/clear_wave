"use client"

import { useState, useEffect, useRef } from "react"
import { format } from "date-fns"
import { MessageSquare } from "lucide-react"
import backendApi from "@/utils/backendApi"
// import MessageInput from "./MessageInput"
import { MessageBubble } from "./MessageBubble"

export default function MessageThread({ caseId, initialMessages = [] }) {
  const [messages, setMessages] = useState(initialMessages)
  const bottomRef = useRef(null)

  // 🔥 FETCH MESSAGES
  const fetchMessages = async () => {
    try {
      const token = localStorage.getItem("authToken")

      const res = await backendApi.get(
        // `/client_management/case_messages/${caseId}/`,
                `/client_management/list_case_messages/${caseId}/`,

        {
          headers: {
            Authorization: `Token ${token}`
          }
        }
      )

      // setMessages(res.data || [])
       // Unwrap proxy response — res.data is { status, data: [...] }
      const data = res.data?.data ?? res.data
      setMessages(Array.isArray(data) ? data : [])
    } catch (err) {
      console.error("Failed to load messages", err)
    }
  }

  useEffect(() => {
    fetchMessages()
  }, [caseId])

  // 🔥 AUTO SCROLL
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // 🔥 SEND MESSAGE
  const handleSend = async (text) => {
    if (!text.trim()) return
    try {
      const token = localStorage.getItem("authToken")

      const res = await backendApi.post(
        `/client_management/send_message/${caseId}/`,
        { content: text },
        { headers: { Authorization: `Token ${token}` } }
      )

      // Unwrap proxy response before pushing to state
      const newMessage = res.data?.data ?? res.data
      setMessages((prev) => [...prev, newMessage])

    } catch (err) {
      console.error("Failed to send message", err)
    }
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-100 flex flex-col">

      {/* Header */}
      <div className="px-5 py-4 border-b border-gray-50">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-gray-400" />
          <h3 className="text-[14px] font-semibold text-gray-900">
            Messages
          </h3>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 px-5 py-4 space-y-4 max-h-80 overflow-y-auto">

        {messages.length === 0 ? (
          <div className="text-center py-8">
            <MessageSquare className="w-7 h-7 text-gray-200 mx-auto mb-2" />
            <p className="text-[13px] text-gray-400">No messages yet.</p>
          </div>
        ) : (
          messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      {/* <div className="px-5 pb-5 pt-3 border-t border-gray-50">
        <MessageInput onSend={handleSend} />
      </div> */}
    </div>
  )
}