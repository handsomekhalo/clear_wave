"use client";

import { useState } from "react";
import UsersTable from "../../components/users/UserTable";
import AddUserModal from "@/components/users/AddUserModal";
import Sidebar from "../../components/layout/SideBar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus } from "lucide-react";


export default function UsersPage({ collapsed, setCollapsed }) {

  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");

  return (
    <div>

      <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />

      <div
        className={`transition-all duration-300 ${
          collapsed ? "ml-[68px]" : "ml-[240px]"
        }`}
      >
        <div className="p-6 space-y-6">

          {/* Header */}
          <div className="flex items-center justify-between">

            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                Team Members
              </h1>

              <p className="text-sm text-gray-500">
                Manage lawyers and assistants in your firm
              </p>
            </div>

            <Button
              onClick={() => setOpen(true)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Plus className="w-4 h-4 mr-1" />
              Add User
            </Button>

          </div>

          {/* Search */}
          <div className="max-w-sm ml-1">
            <Input
              placeholder="Search team member..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          {/* Table */}
          <UsersTable search={search} />

        </div>
      </div>

      {/* Modal */}
      <AddUserModal
        open={open}
        onOpenChange={setOpen}
        onSuccess={() => setOpen(false)}
      />

    </div>
  );
}