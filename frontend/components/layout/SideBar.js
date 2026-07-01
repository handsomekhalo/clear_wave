"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Briefcase,
  FileText,
  Users,
  ClipboardList,
  ChevronLeft,
  ChevronRight,
  Scale,
} from "lucide-react";

const navItems = [
  { name: "Dashboard", icon: LayoutDashboard, path: "/dashboard" },
  { name: "Cases", icon: Briefcase, path: "/cases" },
  { name: "Form Management", icon: ClipboardList, path: "/forms" },
  { name: "Question Management", icon: Users, path: "/questions" },  
  { name: "Manage Users", icon: Users, path: "/users" },
  {name:"Audit Logs", icon: FileText, path: "/audit_log"},
];

export default function Sidebar({ collapsed, setCollapsed }) {
  const pathname = usePathname();

  return (
    <aside
      className={`fixed left-0 top-0 h-full bg-white border-r border-gray-100 z-40 flex flex-col transition-all duration-300 ${
        collapsed ? "w-[68px]" : "w-[240px]"
      }`}
    >
      {/* Logo */}
      <div className="h-16 flex items-center px-5 border-b border-gray-100">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <Scale className="w-4 h-4 text-white" />
          </div>
          {!collapsed && (
            <span className="text-[15px] font-semibold text-gray-900">
              LegalDesk
            </span>
          )}
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 px-3 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname.startsWith(item.path);

          return (
            <Link
              key={item.name}
              href={item.path}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13.5px] font-medium transition-all ${
                isActive
                  ? "bg-blue-50 text-blue-600"
                  : "text-gray-500 hover:text-gray-900 hover:bg-gray-50"
              } ${collapsed ? "justify-center px-0" : ""}`}
            >
              <item.icon
                className={`w-[18px] h-[18px] ${
                  isActive ? "text-blue-600" : "text-gray-400"
                }`}
                strokeWidth={1.8}
              />
              {!collapsed && <span>{item.name}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Collapse Toggle */}
      <div className="p-3 border-t border-gray-100">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="w-full text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-md p-2 flex items-center justify-center"
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <>
              <ChevronLeft className="w-4 h-4 mr-2" />
              <span className="text-xs">Collapse</span>
            </>
          )}
        </button>
      </div>
    </aside>
  );
}