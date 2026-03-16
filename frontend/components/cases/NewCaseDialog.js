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
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const defaultForm = {
  title: "",
  client_name: "",
  status: "active",
  assigned_lawyer: "",
  deadline: "",
  case_number: "",
  description: "",
  case_type: "",
};

export default function NewCaseDialog({
  open,
  onOpenChange,
  onSave,
  editingCase,
}) {
  const [form, setForm] = useState(defaultForm);

  useEffect(() => {
    if (editingCase) {
      setForm({ ...defaultForm, ...editingCase });
    } else {
      setForm(defaultForm);
    }
  }, [editingCase, open]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(form, editingCase?.id);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[520px] p-0 gap-0 rounded-xl">
        <DialogHeader className="px-6 pt-6 pb-4 border-b border-gray-100">
          <DialogTitle className="text-[16px] font-semibold text-gray-900">
            {editingCase ? "Edit Case" : "New Case"}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2 space-y-1.5">
              <Label>Case Title</Label>
              <Input
                value={form.title}
                onChange={(e) =>
                  setForm({ ...form, title: e.target.value })
                }
                required
              />
            </div>

            <div className="space-y-1.5">
              <Label>Client Name</Label>
              <Input
                value={form.client_name}
                onChange={(e) =>
                  setForm({ ...form, client_name: e.target.value })
                }
                required
              />
            </div>

            <div className="space-y-1.5">
              <Label>Case Number</Label>
              <Input
                value={form.case_number}
                onChange={(e) =>
                  setForm({ ...form, case_number: e.target.value })
                }
              />
            </div>

            <div className="space-y-1.5">
              <Label>Status</Label>
              <Select
                value={form.status}
                onValueChange={(v) =>
                  setForm({ ...form, status: v })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="closed">Closed</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <Label>Assigned Lawyer</Label>
              <Input
                value={form.assigned_lawyer}
                onChange={(e) =>
                  setForm({
                    ...form,
                    assigned_lawyer: e.target.value,
                  })
                }
              />
            </div>

            <div className="space-y-1.5">
              <Label>Deadline</Label>
              <Input
                type="date"
                value={form.deadline}
                onChange={(e) =>
                  setForm({ ...form, deadline: e.target.value })
                }
              />
            </div>

            <div className="col-span-2 space-y-1.5">
              <Label>Description</Label>
              <Textarea
                value={form.description}
                onChange={(e) =>
                  setForm({ ...form, description: e.target.value })
                }
              />
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button
              type="button"
              variant="ghost"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit">
              {editingCase ? "Save Changes" : "Create Case"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}