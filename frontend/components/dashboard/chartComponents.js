"use client"

import { useEffect, useState } from "react"
import {
  BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Rectangle
} from "recharts"
import backendApi from "../../lib/backendApi"

const STATUS_COLORS = {
  new:      "#3B82F6",
  active:   "#10B981",
  on_hold:  "#F59E0B",
  closed:   "#6B7280",
  archived: "#D1D5DB",
}

// Custom shape component to dynamically resolve colors per bar slice without <Cell />
const CustomBarShape = (props) => {
  console.log("BAR PROPS", props)

  const status = props.payload?.status
  const fillColor = STATUS_COLORS[status] ?? "#3B82F6"

  return <Rectangle {...props} fill={fillColor} />
}

export default function DashboardCharts() {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetch = async () => {
      try {
        const token = localStorage.getItem("authToken")

        const res = await backendApi.get(
          '/case_management/dashboard_stats/',
          { headers: { Authorization: `Token ${token}` } }
        )
        const dashaboard_data = res.data?.data ?? res.data
        console.log("Dashboard stats response: ", dashaboard_data)
        setData(dashaboard_data)
      } catch (err) {
        console.error("Dashboard stats failed", err)
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [])

  if (loading) return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
      {[1,2].map(i => (
        <div key={i} className="bg-white border border-slate-200 rounded-2xl p-6 h-64 flex items-center justify-center">
          <p className="text-sm text-slate-400">Loading...</p>
        </div>
      ))}
    </div>
  )

  if (!data) return null

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

      {/* Cases by Status */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6">
        <h3 className="text-sm font-semibold text-slate-900 mb-4">Cases by Status</h3>
          <div style={{ width: "100%", height: 208 }}> 
          {data.cases_by_status?.length === 0 ? (
            <div className="flex items-center justify-center h-full text-sm text-slate-400">
              No cases yet.
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data.cases_by_status}
                margin={{ top: 4, right: 8, left: -12, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                <XAxis
                  dataKey="status"
                  tick={{ fontSize: 11, fill: "#94A3B8" }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={v => v.replace("_", " ")}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: "#94A3B8" }}
                  tickLine={false}
                  axisLine={false}
                  allowDecimals={false}
                />
                <Tooltip
                  formatter={(value) => [value, "Cases"]}
                  labelFormatter={(l) => l.replace("_", " ")}
                  contentStyle={{ borderRadius: 8, border: "1px solid #E2E8F0", fontSize: 12 }}
                />
                {/* Replaced <Cell /> mapping with future-proof shape prop */}
                <Bar
  dataKey="count"
  fill="#3B82F6"
  radius={[4,4,0,0]}
  maxBarSize={48}
/>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Cases over time */}
<div className="bg-white border border-slate-200 rounded-2xl p-6">
  <h3 className="text-sm font-semibold text-slate-900 mb-4">Cases Opened — Last 30 Days</h3>
    <div style={{ width: "100%", height: 208 }}>  {/* same fix */}
          {data.cases_over_time?.length === 0 ? (
            <div className="flex items-center justify-center h-full text-sm text-slate-400">
              No activity in the last 30 days.
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={data.cases_over_time}
                margin={{ top: 4, right: 8, left: -12, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 10, fill: "#94A3B8" }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={v => {
                    const d = new Date(v)
                    return `${d.getDate()}/${d.getMonth()+1}`
                  }}
                  interval="preserveStartEnd"
                />
                <YAxis
                  tick={{ fontSize: 11, fill: "#94A3B8" }}
                  tickLine={false}
                  axisLine={false}
                  allowDecimals={false}
                />
                <Tooltip
                  formatter={(value) => [value, "Cases"]}
                  labelFormatter={(l) => new Date(l).toLocaleDateString("en-ZA", { dateStyle: "medium" })}
                  contentStyle={{ borderRadius: 8, border: "1px solid #E2E8F0", fontSize: 12 }}
                />
                <Line
                  type="monotone"
                  dataKey="count"
                  stroke="#3B82F6"
                  strokeWidth={2}
                  dot={{ fill: "#3B82F6", r: 3 }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

    </div>
  )
}
