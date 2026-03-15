"use client";

import { useEffect, useState } from "react";
import { getFirmUserDetails } from "../../lib/api/firm_users";
import Sidebar from '../../components/layout/SideBar';
import {getFirmUsers, } from "../../lib/api/firm_users";
import { ManageUserMenu } from "./ManageUserMenu";
import { ViewUserModal } from "./ViewUserModal";

// import {getFirmUserDetails} from "../../lib/api/firm_users";

export default function UsersTable({ search }) {

  const [users, setUsers] = useState([]);
  const [collapsed, setCollapsed] = useState(false);
  const [viewUser, setViewUser] = useState(null)
  const [viewOpen, setViewOpen] = useState(false)

  useEffect(() => {

    const fetchUsers = async () => {
      try {
        const res = await getFirmUsers();
        setUsers(res.data); // 👈 FIX
      } catch (err) {
        console.error("Failed to fetch users", err);
      }
    };

    fetchUsers();

  }, []);

  const filteredUsers = users.filter((u) =>
    `${u.first_name} ${u.last_name} ${u.email}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );


 const handleViewUser = async (user) => {

  console.log("USER:", user)

  const data = await getFirmUserDetails(user.id)

  setViewUser(data.data)
  setViewOpen(true)
}

const handleToggleStatus = (user) => {
  console.log("toggle user", user)
}


return (
  <div>

    {/* Sidebar */}
    <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />

    {/* Main content */}
    <div
      // className={`transition-all duration-300 ${
      //   collapsed ? "ml-[1px]" : "ml-1px]"
      // }`}
    >
      <div className="">

        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">

          <div className="overflow-x-auto">

            <table className="w-full text-sm">

              <thead className="bg-gray-50 border-b">
                <tr className="text-gray-600 text-xs uppercase tracking-wide">
                  <th className="px-6 py-3 text-left">User</th>
                  <th className="px-6 py-3 text-left">Role</th>
                  <th className="px-6 py-3 text-left">Status</th>
                  <th className="px-6 py-3 text-right">Actions</th>
                </tr>
              </thead>

              <tbody>
                {filteredUsers.map((user) => (
                  <tr key={user.id} className="border-b hover:bg-gray-50 transition">

                    <td className="px-6 py-4 flex items-center gap-3">

                      <div className="w-9 h-9 rounded-full bg-gray-200 flex items-center justify-center text-xs font-medium">
                        {user.first_name?.[0]}
                        {user.last_name?.[0]}
                      </div>

                      <div>
                        <p className="font-medium text-gray-900">
                          {user.first_name} {user.last_name}
                        </p>

                        <p className="text-xs text-gray-500">
                          {user.email}
                        </p>
                      </div>

                    </td>

                    <td className="px-6 py-4 capitalize text-gray-700">

                      {user.role}
                    </td>

                    <td className="px-6 py-4">
                      {user.is_active ? (
                        <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-md">
                          Active
                        </span>
                      ) : (
                        <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-md">
                          Inactive
                        </span>
                      )}
                    </td>

                      <td className="px-6 py-4 text-right">
                    <ManageUserMenu
                      user={user}
                      onView={handleViewUser}
                      onToggleStatus={handleToggleStatus}
                    />
                  </td>

                  </tr>
                ))}
              </tbody>

            </table>

          </div>

          {filteredUsers.length === 0 && (
            <div className="p-8 text-center text-sm text-gray-500">
              No users found
            </div>
          )}

        </div>

      </div>
    </div>
      <ViewUserModal
        open={viewOpen}
        onOpenChange={setViewOpen}
        user={viewUser}
      />
  </div>
  
)
}