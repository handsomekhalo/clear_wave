"use client";

// components/cases/StatusBadge.js

const STATUS_DISPLAY = {
  new: "New",
  pending: "Pending",
  active: "Active",
  closed: "Closed",
};

const STATUS_STYLES = {
  new:     "bg-yellow-100 text-yellow-800",
  pending: "bg-orange-100 text-orange-800",
  active:  "bg-green-100 text-green-800",
  closed:  "bg-gray-100 text-gray-600",
};

export default function StatusBadge({ status }) {
  const key = status?.toLowerCase() ?? "";
  const label = STATUS_DISPLAY[key] ?? (status ? status.charAt(0).toUpperCase() + status.slice(1) : "—");
  const style = STATUS_STYLES[key] ?? "bg-gray-100 text-gray-600";
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${style}`}>
      {label}
    </span>
  );
}


// "use client";

// const statusConfig = {
//   active: {
//     label: "Active",
//     bg: "bg-emerald-50",
//     text: "text-emerald-700",
//     dot: "bg-emerald-500",
//   },
//   closed: {
//     label: "Closed",
//     bg: "bg-gray-50",
//     text: "text-gray-500",
//     dot: "bg-gray-400",
//   },
//   pending: {
//     label: "Pending",
//     bg: "bg-amber-50",
//     text: "text-amber-700",
//     dot: "bg-amber-500",
//   },
// };

// export default function StatusBadge({ status }) {
//   const config = statusConfig[status] || statusConfig.pending;

//   return (
//     <span
//       className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[12px] font-medium ${config.bg} ${config.text}`}
//     >
//       <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />
//       {config.label}
//     </span>
//   );
// }