"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

export default function FirmUserModal({
  open,
  onOpenChange,
  user,
}) {
  if (!user) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>

        <DialogHeader>
          <DialogTitle>User Details</DialogTitle>
        </DialogHeader>

        <div className="space-y-3 text-sm">

          <Row label="Name">
            {user.first_name} {user.last_name}
          </Row>

          <Row label="Email">{user.email}</Row>

          <Row label="Role">{user.role}</Row>

          <Row label="Phone">
            {user.phone_number || "—"}
          </Row>

          <Row label="Status">
            {user.is_active ? "Active" : "Inactive"}
          </Row>

        </div>

      </DialogContent>
    </Dialog>
  );
}

function Row({ label, children }) {
  return (
    <div className="flex justify-between border-b pb-2">
      <span className="text-gray-500">{label}</span>
      <span className="font-medium">{children}</span>
    </div>
  );
}