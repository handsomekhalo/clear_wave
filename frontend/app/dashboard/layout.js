"use client";


import { useState } from "react";
import { Menu } from "lucide-react";
import  Sidebar from '../../components/layout/SideBar';
import MobileNav from "@/components/layout/MobileNav";


export default function DashboardLayout({ children }) {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#FAFAFA]">
      <div className="hidden lg:block">
        <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />
      </div>

      <MobileNav open={mobileOpen} setOpen={setMobileOpen} />

      <div
        className={`transition-all duration-300 ${
          collapsed ? "lg:ml-[68px]" : "lg:ml-[240px]"
        }`}
      >
        <div className="lg:hidden h-14 bg-white border-b border-gray-100 flex items-center px-4">
          <button
            className="h-9 w-9 text-gray-500"
            onClick={() => setMobileOpen(true)}
          >
            <Menu className="w-5 h-5" />
          </button>
        </div>

        <main className="min-h-screen">{children}</main>
      </div>
    </div>
  );
}