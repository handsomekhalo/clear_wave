"use client";

import { Briefcase, CheckCircle, Clock, Users } from "lucide-react";

export default function StatsCards({ cases = [] }) {

  const active = cases.filter((c) => c.status === "active").length;
  const closed = cases.filter((c) => c.status === "closed").length;
  const pending = cases.filter((c) => c.status === "pending").length;
  const uniqueClients = new Set(cases.map((c) => c.client_name)).size;

  const stats = [
    {
      label: "Total Cases",
      value: cases.length,
      icon: Briefcase,
      color: "text-blue-600",
      bg: "bg-blue-50",
    },
    {
      label: "Active",
      value: active,
      icon: Clock,
      color: "text-emerald-600",
      bg: "bg-emerald-50",
    },
    {
      label: "Closed",
      value: closed,
      icon: CheckCircle,
      color: "text-gray-500",
      bg: "bg-gray-50",
    },
    {
      label: "Clients",
      value: uniqueClients,
      icon: Users,
      color: "text-violet-600",
      bg: "bg-violet-50",
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((s) => (
        <div
          key={s.label}
          className="bg-white rounded-xl border border-gray-100 p-5"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-[12px] font-medium text-gray-400 uppercase tracking-wider">
              {s.label}
            </span>
            <div
              className={`w-8 h-8 rounded-lg ${s.bg} flex items-center justify-center`}
            >
              <s.icon
                className={`w-4 h-4 ${s.color}`}
                strokeWidth={1.8}
              />
            </div>
          </div>

          <span className="text-[28px] font-semibold text-gray-900 tracking-tight">
            {s.value}
          </span>
        </div>
      ))}
    </div>
  );
}