'use client'

import { useState, useEffect } from "react";
import SideBar from "@/components/layout/SideBar";
import TopBar from "@/components/layout/TopBar";
import StatsCards from "../../components/dashboard/StartsCard";
import DashboardCharts from "../../components/dashboard/chartComponents";
import SubscriptionBanner from "../../components/layout/SubscriptionBanner";
import { getAllCases } from "../../lib/api/cases";

export default function DashboardPage() {
  const [collapsed, setCollapsed] = useState(false);
  const [cases, setCases] = useState([]);

  useEffect(() => {
    getAllCases()
      .then(res => setCases(Array.isArray(res) ? res : res.data ?? []))
      .catch(err => console.error("Failed to load cases", err));
  }, []);

  return (
    <div className="flex">
      <SideBar collapsed={collapsed} setCollapsed={setCollapsed} />
      <main className={`flex-1 transition-all duration-300 ${
        collapsed ? "ml-[68px]" : "ml-[240px]"
      }`}>
        <TopBar title="Dashboard" />
        <SubscriptionBanner />
        <div className="p-6">
          <StatsCards cases={cases} />
          <DashboardCharts />
        </div>
      </main>
    </div>
  );
}