"use client";

import { useState, useEffect } from "react";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { Loader2 } from "lucide-react";
import { updateFirmUser } from "@/lib/api/firmUsersApi";

export default function EditUserModal({
  open,
  onOpenChange,
  user,
  onSuccess,
}) {
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    role: "",
    phone_number: "",
  });

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      setForm({
        first_name: user.first_name || "",
        last_name: user.last_name || "",
        role: user.role || "",
        phone_number: user.phone_number || "",
      });
    }
  }, [user]);

  const set = (k, v) =>
    setForm((f) => ({ ...f, [k]: v }));

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);

    try {
      await updateFirmUser(user.id, form);

      onSuccess?.("User updated");

      onOpenChange(false);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>

        <DialogHeader>
          <DialogTitle>Edit User</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">

          <Field label="Email">
            <Input value={user.email} disabled />
          </Field>

          <div className="grid grid-cols-2 gap-3">

            <Field label="First Name">
              <Input
                value={form.first_name}
                onChange={(e) =>
                  set("first_name", e.target.value)
                }
              />
            </Field>

            <Field label="Last Name">
              <Input
                value={form.last_name}
                onChange={(e) =>
                  set("last_name", e.target.value)
                }
              />
            </Field>

          </div>

          <Field label="Role">

            <Select
              value={form.role}
              onValueChange={(v) => set("role", v)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>

              <SelectContent>
                <SelectItem value="lawyer">Lawyer</SelectItem>
                <SelectItem value="assistant">
                  Assistant
                </SelectItem>
              </SelectContent>
            </Select>

          </Field>

          <Field label="Phone Number">
            <Input
              value={form.phone_number}
              onChange={(e) =>
                set("phone_number", e.target.value)
              }
            />
          </Field>

          <div className="flex justify-end gap-2">

            <Button
              variant="ghost"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>

            <Button type="submit" disabled={loading}>
              {loading && (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              )}
              Save Changes
            </Button>

          </div>

        </form>

      </DialogContent>
    </Dialog>
  );
}

function Field({ label, children }) {
  return (
    <div className="space-y-1">
      <Label>{label}</Label>
      {children}
    </div>
  );
}