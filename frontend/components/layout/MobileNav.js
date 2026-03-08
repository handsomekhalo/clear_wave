"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Briefcase,
  FileText,
  Users,
  ClipboardList,
  X,
  Scale,
} from "lucide-react";

const navItems = [
  { name: "Dashboard", icon: LayoutDashboard, path: "/dashboard" },
  { name: "Cases", icon: Briefcase, path: "/cases" },
  { name: "Documents", icon: FileText, path: "/documents" },
  { name: "Clients", icon: Users, path: "/clients" },
  { name: "Forms", icon: ClipboardList, path: "/forms" },
];

export default function MobileNav({ open, setOpen }) {
  const pathname = usePathname();
  if (!open) return null;

  return (
    <>
      <div
        className="fixed inset-0 bg-black/20 z-40 lg:hidden"
        onClick={() => setOpen(false)}
      />

      <div className="fixed left-0 top-0 h-full w-[260px] bg-white z-50 shadow-xl lg:hidden">
        <div className="h-16 flex items-center justify-between px-5 border-b border-gray-100">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
              <Scale className="w-4 h-4 text-white" />
            </div>
            <span className="text-[15px] font-semibold text-gray-900">
              LegalDesk
            </span>
          </div>

          <button onClick={() => setOpen(false)}>
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        <nav className="py-4 px-3 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname.startsWith(item.path);

            return (
              <Link
                key={item.name}
                href={item.path}
                onClick={() => setOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13.5px] font-medium ${
                  isActive
                    ? "bg-blue-50 text-blue-600"
                    : "text-gray-500 hover:text-gray-900 hover:bg-gray-50"
                }`}
              >
                <item.icon
                  className={`w-[18px] h-[18px] ${
                    isActive ? "text-blue-600" : "text-gray-400"
                  }`}
                  strokeWidth={1.8}
                />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </>
  );
}