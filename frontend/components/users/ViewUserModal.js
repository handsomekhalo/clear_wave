'use client'


import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import FetchUserRoles from "../hooks/fetchroles"

export function ViewUserModal({ open, onOpenChange, user }) {

  // const { roles, loading } = useRoles()
    const { roles, loading } = FetchUserRoles()
    

  if (!user) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>

      <DialogContent className="sm:max-w-[500px]">

        <DialogHeader>
          <DialogTitle>User Details</DialogTitle>
        </DialogHeader>

        <div className="space-y-3">

          <div>
            <Label>First Name</Label>
            <Input defaultValue={user.first_name} />
          </div>

          <div>
            <Label>Last Name</Label>
            <Input defaultValue={user.last_name} />
          </div>

          <div>
            <Label>Email</Label>
            <Input defaultValue={user.email} disabled />
          </div>

          <div>
            <Label>Role</Label>

            {loading ? (
              <Input disabled value="Loading roles..." />
            ) : (
              <select
                defaultValue={user.role}
                className="w-full border rounded-md px-3 py-2"
              >
                {roles.map((role) => (
                  <option key={role.key} value={role.key}>
                    {role.label}
                  </option>
                ))}
              </select>
            )}

          </div>

          <div>
            <Label>Phone</Label>
            <Input defaultValue={user.phone} />
          </div>

        </div>

        <div className="flex justify-end gap-2 mt-4">

          <Button variant="ghost" onClick={() => onOpenChange(false)}>
            Close
          </Button>

          <Button>
            Save Changes
          </Button>

        </div>

      </DialogContent>

    </Dialog>
  )
}


function Field({ label, error, children }) {
  return (
    <div className="space-y-1">
      <Label>{label}</Label>
      {children}
      {error && (
        <p className="text-xs text-red-500">{error}</p>
      )}
    </div>
  )
}