'use client'


import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import FetchUserRoles from "../hooks/fetchroles"

import { useState, useEffect } from "react"
// import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
// import { Input } from "@/components/ui/input"
// import { Label } from "@/components/ui/label"
// import { Button } from "@/components/ui/button"

import { updateFirmUser } from "../../lib/api/firm_users"

export function ViewUserModal({ open, onOpenChange, user, onSuccess }) {

  const { roles, loading } = FetchUserRoles()

  const [form, setForm] =useState ({
    first_name: "",
    last_name: "",
    phone: "",
    role: ""
  })

  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (user) {
      setForm({
        first_name: user.first_name || "",
        last_name: user.last_name || "",
        phone: user.phone || "",
        role: user.role || ""
      })
    }
  }, [user])

  const set = (key, value) => {
    setForm((prev) => ({
      ...prev,
      [key]: value
    }))
  }

  const handleSave = async () => {

    try {

      setSaving(true)
          console.log()


      await updateFirmUser(user.id, form)


      if (onSuccess) onSuccess()

      onOpenChange(false)

    } catch (err) {

      console.error("Update failed", err)

    } finally {
      setSaving(false)
    }
  }

  if (!user) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>

      <DialogContent className="sm:max-w-[500px]">

        <DialogHeader>
          <DialogTitle>Edit User</DialogTitle>
        </DialogHeader>

        <div className="space-y-3">

          <div>
            <Label>First Name</Label>
            <Input
              value={form.first_name}
              onChange={(e) => set("first_name", e.target.value)}
            />
          </div>

          <div>
            <Label>Last Name</Label>
            <Input
              value={form.last_name}
              onChange={(e) => set("last_name", e.target.value)}
            />
          </div>

          <div>
            <Label>Email</Label>
            <Input value={user.email} disabled />
          </div>

          <div>
            <Label>Role</Label>

            {loading ? (
              <Input disabled value="Loading roles..." />
            ) : (
              <select
                value={form.role}
                onChange={(e) => set("role", e.target.value)}
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
            <Input
              value={form.phone}
              onChange={(e) => set("phone", e.target.value)}
            />
          </div>

        </div>

        <div className="flex justify-end gap-2 mt-4">

          <Button
            variant="ghost"
            onClick={() => onOpenChange(false)}
          >
            Close
          </Button>

          <Button
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? "Saving..." : "Save Changes"}
          </Button>

        </div>

      </DialogContent>

    </Dialog>
  )
}
