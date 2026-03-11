"use client";

import { useState } from "react";
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
import { createFirmUser } from "../../lib/api/firm_users";

const defaultForm = {
  first_name: "",
  last_name: "",
  email: "",
  role: "",
  phone_number: "",
};

export default function AddUserModal({ open, onOpenChange, onSuccess }) {
  const [form, setForm] = useState(defaultForm);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const set = (k, v) => {
    setForm((f) => ({ ...f, [k]: v }));
    setErrors((e) => ({ ...e, [k]: undefined }));
  };

  const validate = () => {
    const e = {};

    if (!form.first_name.trim()) e.first_name = "Required";
    if (!form.last_name.trim()) e.last_name = "Required";

    if (!form.email.trim()) e.email = "Required";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email))
      e.email = "Invalid email";

    if (!form.role) e.role = "Required";

    return e;
  };

  const handleSubmit = async (ev) => {
    ev.preventDefault();

    const e = validate();
    if (Object.keys(e).length) {
      setErrors(e);
      return;
    }

    setLoading(true);

    try {
      await createFirmUser(form);

      setForm(defaultForm);
      setErrors({});

      onSuccess?.("User invited successfully");

      onOpenChange(false);
    } catch (err) {
      setErrors({
        _general: "Something went wrong. Please try again.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog
      open={open}
      onOpenChange={(o) => {
        if (!loading) {
          onOpenChange(o);
          if (!o) {
            setForm(defaultForm);
            setErrors({});
          }
        }
      }}
    >
      <DialogContent className="sm:max-w-[480px]">
        <DialogHeader>
          <DialogTitle>Add Team Member</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">

          {errors._general && (
            <p className="text-sm text-red-500">{errors._general}</p>
          )}

          <div className="grid grid-cols-2 gap-3">

            <Field label="First Name *" error={errors.first_name}>
              <Input
                value={form.first_name}
                onChange={(e) => set("first_name", e.target.value)}
              />
            </Field>

            <Field label="Last Name *" error={errors.last_name}>
              <Input
                value={form.last_name}
                onChange={(e) => set("last_name", e.target.value)}
              />
            </Field>

          </div>

          <Field label="Email *" error={errors.email}>
            <Input
              type="email"
              value={form.email}
              onChange={(e) => set("email", e.target.value)}
            />
          </Field>

          <Field label="Role *" error={errors.role}>
            <Select
              value={form.role}
              onValueChange={(v) => set("role", v)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select role" />
              </SelectTrigger>

              <SelectContent>
                <SelectItem value="lawyer">Lawyer</SelectItem>
                <SelectItem value="assistant">Assistant</SelectItem>
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
              type="button"
              variant="ghost"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>

            <Button type="submit" disabled={loading}>
              {loading && (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              )}
              Send Invite
            </Button>

          </div>

        </form>
      </DialogContent>
    </Dialog>
  );
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
  );
}