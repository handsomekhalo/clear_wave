"use client"

import { useState } from "react"
import { Send } from "lucide-react"

export default function MessageInput({ onSend }) {
  const [text, setText] = useState("")

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!text.trim()) return

    onSend(text)
    setText("")
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex items-end gap-2">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Write a message to your legal team…"
        rows={2}
        className="flex-1 resize-none rounded-xl border border-gray-200 px-4 py-3 text-[13.5px] text-gray-800 placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
      />

      <button
        type="submit"
        disabled={!text.trim()}
        className="w-10 h-10 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:bg-gray-100 flex items-center justify-center"
      >
        <Send className="w-4 h-4 text-white" />
      </button>
    </form>
  )
}