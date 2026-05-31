"use client";

import { useState, useEffect, useCallback } from "react";
import SideBar from "@/components/layout/SideBar";
import TopBar from "@/components/layout/TopBar";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { getAllUsers } from "@/lib/api/users";
import { inviteUser } from "@/lib/api/users";

// Add this import at the top of UsersPage
import { ManageUserMenu } from "../../components/users/ManageUserMenu";
import { ViewUserModal } from "../../components/users/ViewUserModal";
import { getFirmUserDetails } from "../../lib/api/firm_users";


export default function UsersPage() {
  const [users, setUsers]           = useState([]);
  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState(null);
  const [search, setSearch]         = useState("");
  const [open, setOpen]             = useState(false);
  const [collapsed, setCollapsed]   = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [viewUser, setViewUser] = useState(null);
  const [viewOpen, setViewOpen] = useState(false);

  const [form, setForm] = useState({
    first_name: "", last_name: "", email: "", role: "", phone: "",
  });


  const handleViewUser = async (user) => {
  const data = await getFirmUserDetails(user.id);
  setViewUser(data.data);
  setViewOpen(true);
};

const handleToggleStatus = async (user_id) => {
  try {
    await toggleFirmUserStatus(user_id);
    await fetchUsers();
  } catch (err) {
    console.error("Status update failed", err);
  }
};

  // ✅ FIX 1: Fetch users from real API
  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getAllUsers();
      setUsers(Array.isArray(res) ? res : res.data ?? []);
    } catch (err) {
      console.error("Failed to load users", err);
      setError("Failed to load team members.");
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const handleInvite = async () => {
    if (!form.first_name || !form.last_name || !form.email || !form.role) {
      setSubmitError("Please fill in all required fields.");
      return;
    }
    setSubmitting(true);
    setSubmitError(null);
    try {
      await inviteUser(form);
      // ✅ FIX 2: Refresh list after invite so new user appears immediately
      await fetchUsers();
      setOpen(false);
      setForm({ first_name: "", last_name: "", email: "", role: "", phone: "" });
    } catch (err) {
      console.error("Failed to invite user", err);
      setSubmitError("Failed to send invite. Please try again.");
    } finally { setSubmitting(false); }
  };

  const filteredUsers = users.filter(u => {
    const name = u.name || `${u.first_name || ""} ${u.last_name || ""}`.trim();
    const email = u.email || "";
    const q = search.toLowerCase();
    return name.toLowerCase().includes(q) || email.toLowerCase().includes(q);
  });

  const getInitials = (u) => {
    const name = u.name || `${u.first_name || ""} ${u.last_name || ""}`.trim();
    return name.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase() || "??";
  };

  const getDisplayName = (u) => {
    return u.name || `${u.first_name || ""} ${u.last_name || ""}`.trim() || u.email;
  };

  return (
    <div className="flex">
      <SideBar collapsed={collapsed} setCollapsed={setCollapsed} />
      <main className={`flex-1 transition-all duration-300 ${collapsed ? "ml-[68px]" : "ml-[240px]"}`}>
        {/* Header */}
        <div className="flex items-center justify-between px-6 pt-6 pb-2">
          <div>
            <h1 className="text-xl font-semibold">Team Members</h1>
            <p className="text-sm text-gray-500">Manage lawyers and assistants in your firm</p>
          </div>
          <Button onClick={() => { setOpen(true); setSubmitError(null); }}>
            + Add User
          </Button>
        </div>

        {/* Search */}
        <div className="px-6 py-3">
          <Input
            placeholder="Search team member..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="max-w-md"
          />
        </div>

        {/* Table */}
        <div className="px-6 pb-8">
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="flex flex-col items-center gap-3 text-gray-400">
                <svg className="animate-spin h-8 w-8" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                </svg>
                <span className="text-sm">Loading team members...</span>
              </div>
            </div>
          ) : error ? (
            <div className="text-center py-16 text-red-500">
              <p>{error}</p>
              <button onClick={fetchUsers} className="mt-2 text-sm text-blue-600 underline">Try again</button>
            </div>
          ) : (
            <table className="w-full border-collapse">
              <thead>
                <tr className="text-left text-xs text-gray-500 uppercase tracking-wide border-b">
                  <th className="py-3 pr-4">User</th>
                  <th className="py-3 pr-4">Role</th>
                  <th className="py-3 pr-4">Status</th>
                  <th className="py-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="text-center py-12 text-gray-400 text-sm">
                      {search ? "No users found matching your search." : "No team members yet."}
                    </td>
                  </tr>
                ) : (
                  filteredUsers.map((u, i) => (
                    <tr key={u.id ?? i} className="border-b hover:bg-gray-50 transition-colors">
                      <td className="py-3 pr-4">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-full bg-gray-200 flex items-center justify-center text-xs font-semibold text-gray-600 shrink-0">
                            {getInitials(u)}
                          </div>
                          <div>
                            <p className="text-sm font-medium">{getDisplayName(u)}</p>
                            <p className="text-xs text-gray-400">{u.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 pr-4 text-sm capitalize">{u.role?.replace("_", " ") || "—"}</td>
                      <td className="py-3 pr-4">
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                          u.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"
                        }`}>
                          {u.is_active ? "Active" : "Inactive"}
                        </span>
                      </td>
                 

                  <td className="py-3">
                    <ManageUserMenu
                      user={u}
                      onView={handleViewUser}
                      onToggleStatus={handleToggleStatus}
                    />
                  </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}
        </div>

        {/* Add User Dialog */}
        <Dialog open={open} onOpenChange={val => { setOpen(val); if (!val) setSubmitError(null); }}>
          <DialogContent className="sm:max-w-[480px]">
            <DialogHeader>
              <DialogTitle>Add Team Member</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-2">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <Label>First Name *</Label>
                  <Input
                    value={form.first_name}
                    onChange={e => setForm({ ...form, first_name: e.target.value })}
                    placeholder="First name"
                  />
                </div>
                <div className="space-y-1">
                  <Label>Last Name *</Label>
                  <Input
                    value={form.last_name}
                    onChange={e => setForm({ ...form, last_name: e.target.value })}
                    placeholder="Last name"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <Label>Email *</Label>
                <Input
                  type="email"
                  value={form.email}
                  onChange={e => setForm({ ...form, email: e.target.value })}
                  placeholder="email@example.com"
                />
              </div>

              <div className="space-y-1">
                <Label>Role *</Label>
                <Select value={form.role} onValueChange={v => setForm({ ...form, role: v })}>
                  <SelectTrigger><SelectValue placeholder="Select role" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="lawyer">Lawyer</SelectItem>
                    <SelectItem value="assistant">Assistant</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-1">
                <Label>Phone Number</Label>
                <Input
                  value={form.phone}
                  onChange={e => setForm({ ...form, phone: e.target.value })}
                  placeholder="e.g. 0731234567"
                />
              </div>

              {submitError && (
                <p className="text-sm text-red-500">{submitError}</p>
              )}

              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
                <Button onClick={handleInvite} disabled={submitting}>
                  {submitting ? "Sending..." : "Send Invite"}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
        <ViewUserModal
  open={viewOpen}
  onOpenChange={setViewOpen}
  user={viewUser}
  onSuccess={fetchUsers}
/>
      </main>
    </div>
  );
}

// export default function UsersPage({ collapsed, setCollapsed }) {

//   const [open, setOpen] = useState(false);
//   const [search, setSearch] = useState("");

//   return (
//     <div>

//       <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />

//       <div
//         className={`transition-all duration-300 ${
//           collapsed ? "ml-[68px]" : "ml-[240px]"
//         }`}
//       >
//         <div className="p-6 space-y-6">

//           {/* Header */}
//           <div className="flex items-center justify-between">

//             <div>
//               <h1 className="text-xl font-semibold text-gray-900">
//                 Team Members
//               </h1>

//               <p className="text-sm text-gray-500">
//                 Manage lawyers and assistants in your firm
//               </p>
//             </div>

//             <Button
//               onClick={() => setOpen(true)}
//               className="bg-blue-600 hover:bg-blue-700"
//             >
//               <Plus className="w-4 h-4 mr-1" />
//               Add User
//             </Button>

//           </div>

//           {/* Search */}
//           <div className="max-w-sm ml-1">
//             <Input
//               placeholder="Search team member..."
//               value={search}
//               onChange={(e) => setSearch(e.target.value)}
//             />
//           </div>

//           {/* Table */}
//           <UsersTable search={search} />

//         </div>
//       </div>

//       {/* Modal */}
//       <AddUserModal
//         open={open}
//         onOpenChange={setOpen}
//         onSuccess={() => setOpen(false)}
//       />

//     </div>
//   );
// }