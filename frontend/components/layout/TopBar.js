"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Bell, Plus, ChevronDown, LogOut, CreditCard, User } from "lucide-react";
import NewCaseDialog from "../cases/NewCaseDialog";
import { createCase } from "../../lib/api/cases";

export default function TopBar({ title }) {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [open, setOpen] = useState(false);
  const [caseOpen, setCaseOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    // Load real user from localStorage
    try {
      const stored = localStorage.getItem("user");
      if (stored) setUser(JSON.parse(stored));
    } catch {
      setUser(null);
    }
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const handleCreateCase = async (data) => {
    try {
      await createCase(data);
      setCaseOpen(false);
    } catch (err) {
      console.error("Failed to create case", err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    localStorage.removeItem("user");
    localStorage.removeItem("csrfToken");
    router.push("/login");
  };

  const initials = user?.first_name && user?.last_name
    ? `${user.first_name[0]}${user.last_name[0]}`.toUpperCase()
    : user?.email?.[0]?.toUpperCase() ?? "U";

  const displayName = user?.first_name && user?.last_name
    ? `${user.first_name} ${user.last_name}`
    : user?.email ?? "User";

  return (
    <header className="h-16 bg-white border-b border-gray-100 flex items-center justify-between px-6 lg:px-8">
      <h1 className="text-[17px] font-semibold text-gray-900 tracking-tight">
        {title}
      </h1>

      <div className="flex items-center gap-2 relative">
        {/* New Case */}
        <button
          onClick={() => setCaseOpen(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white text-[13px] font-medium h-9 px-4 rounded-lg flex items-center"
        >
          <Plus className="w-4 h-4 mr-1.5" />
          New Case
        </button>

        {/* Notifications */}
        <button className="relative h-9 w-9 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-lg flex items-center justify-center">
          <Bell className="w-[18px] h-[18px]" strokeWidth={1.8} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-600 rounded-full" />
        </button>

        {/* User Dropdown */}
        {/* <div className="relative" ref={dropdownRef}> */}
            <div className="relative" ref={dropdownRef}>

          <button
            onClick={() => setOpen(!open)}
            className="h-9 gap-2 px-2 hover:bg-gray-50 rounded-lg flex items-center"
          >
            <div className="w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center">
              <span className="text-[11px] font-semibold text-gray-600">
                {initials}
              </span>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-gray-400" />
          </button>

          {open && (
            <div className="absolute right-0 mt-2 w-52 bg-white border border-gray-100 rounded-lg shadow-md z-50">
              {/* User info */}
              <div className="px-3 py-2.5">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
                    <span className="text-[11px] font-semibold text-blue-600">
                      {initials}
                    </span>
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {displayName}
                    </p>
                    <p className="text-xs text-gray-400 truncate">
                      {user?.email ?? ""}
                    </p>
                  </div>
                </div>
              </div>

              <div className="border-t border-gray-100" />

              {/* Plans */}
              <button
                onClick={() => {
                  setOpen(false);
                  router.push("/subscription/plans");
                }}
                className="w-full text-left px-3 py-2 text-[13px] text-gray-600 hover:bg-gray-50 flex items-center"
              >
                <CreditCard className="w-4 h-4 mr-2 text-gray-400" />
                Plans & Billing
              </button>

              <div className="border-t border-gray-100" />

              {/* Logout */}
              <button
                onClick={handleLogout}
                className="w-full text-left px-3 py-2 text-[13px] text-red-600 hover:bg-red-50 flex items-center rounded-b-lg"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Sign out
              </button>
            </div>
          )}
        </div>
      </div>

      <NewCaseDialog
        open={caseOpen}
        onOpenChange={setCaseOpen}
        onSave={handleCreateCase}
      />
    </header>
  );
}