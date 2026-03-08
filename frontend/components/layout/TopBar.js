"use client";

import { useState, useEffect } from "react";
import { Bell, Plus, ChevronDown, LogOut, Settings, User } from "lucide-react";

export default function TopBar({ title, onNewCase }) {
  const [user, setUser] = useState(null);
  const [open, setOpen] = useState(false);

  // 🔁 Replace this later with your Django auth API
  useEffect(() => {
    // Example placeholder user
    setUser({
      full_name: "Titus Monaheng",
      email: "titus@email.com",
    });
  }, []);

  const initials = user?.full_name
    ? user.full_name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "U";

  return (
    <header className="h-16 bg-white border-b border-gray-100 flex items-center justify-between px-6 lg:px-8">

      <h1 className="text-[17px] font-semibold text-gray-900 tracking-tight">
        {title}
      </h1>

      <div className="flex items-center gap-2 relative">
        {onNewCase && (
          <button
            onClick={onNewCase}
            className="bg-blue-600 hover:bg-blue-700 text-white text-[13px] font-medium h-9 px-4 rounded-lg flex items-center"
          >
            <Plus className="w-4 h-4 mr-1.5" />
            New Case
          </button>
        )}

        {/* Notification */}
        <button className="relative h-9 w-9 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-lg flex items-center justify-center">
          <Bell className="w-[18px] h-[18px]" strokeWidth={1.8} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-600 rounded-full" />
        </button>

        {/* User Dropdown */}
        <div className="relative">
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
            <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-100 rounded-lg shadow-md z-50">
              <div className="px-3 py-2">
                <p className="text-sm font-medium text-gray-900">
                  {user?.full_name || "User"}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {user?.email || ""}
                </p>
              </div>

              <div className="border-t border-gray-100" />

              <button className="w-full text-left px-3 py-2 text-[13px] text-gray-600 hover:bg-gray-50 flex items-center">
                <User className="w-4 h-4 mr-2" />
                Profile
              </button>

              <button className="w-full text-left px-3 py-2 text-[13px] text-gray-600 hover:bg-gray-50 flex items-center">
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </button>

              <div className="border-t border-gray-100" />

              <button
                className="w-full text-left px-3 py-2 text-[13px] text-red-600 hover:bg-gray-50 flex items-center"
                onClick={() => console.log("logout")}
              >
                <LogOut className="w-4 h-4 mr-2" />
                Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}