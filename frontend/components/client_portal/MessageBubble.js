export function MessageBubble({ message }) {
  const isClient = message.sender_role === "client" || message.sender === "client"

  return (
    <div className={`flex ${isClient ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[78%] flex flex-col gap-1`}>

        {!isClient && (
          <span className="text-[11.5px] text-gray-500 px-1">
            Legal Team
          </span>
        )}

        <div
          className={`px-4 py-2.5 rounded-2xl text-[13.5px] ${
            isClient
              ? "bg-blue-600 text-white rounded-br-md"
              : "bg-gray-100 text-gray-800 rounded-bl-md"
          }`}
        >
          {message.content || message.text}
        </div>

        <span className="text-[11px] text-gray-300 px-1">
          {message.created_at
            ? format(new Date(message.created_at), "MMM d, h:mm a")
            : ""}
        </span>

      </div>
    </div>
  )
}