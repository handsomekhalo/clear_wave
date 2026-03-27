"use client"

export default function ClientStatusBadge({ status }) {
  const config = {
    active: {
      label: "Active",
      classes: "bg-emerald-50 text-emerald-700",
      dot: "bg-emerald-500"
    },
    closed: {
      label: "Closed",
      classes: "bg-gray-100 text-gray-500",
      dot: "bg-gray-400"
    },
    pending: {
      label: "Pending",
      classes: "bg-amber-50 text-amber-700",
      dot: "bg-amber-400"
    }
  }

  const s = config[status] || config.pending

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[12px] font-medium ${s.classes}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${s.dot}`} />
      {s.label}
    </span>
  )
}