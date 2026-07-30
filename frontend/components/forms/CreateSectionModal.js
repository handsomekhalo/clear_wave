// components/forms/CreateSectionModal.js
// Stripped from dynamic_forms CategoryModal.js
// Removed: useAuth, AuthContext
// Added: local state, calls createFormSection from lib/api/forms.js
// This modal is triggered from ManageTemplateModal when user clicks "Add Section"

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { createFormSection } from "../../lib/api/forms";

export default function CreateSectionModal({ templateId, onClose, onSuccess }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [order, setOrder] = useState(0);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!name.trim()) {
      setError("Section name is required.");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      await createFormSection(templateId, {
        name: name.trim(),
        description: description.trim(),
        order,
        is_active: true,
      });

      // Tell parent to refresh then close
      onSuccess();
      onClose();
    } catch (err) {
      console.error("Failed to create section:", err);
      setError(
        err?.response?.data?.name?.[0] ||
        err?.response?.data?.detail ||
        "Failed to create section."
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
        <h3 className="text-lg font-semibold mb-4">Add Section</h3>

        {error && (
          <div className="mb-4 rounded bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-600">
            {error}
          </div>
        )}

        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Section Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              placeholder="e.g. Personal Details"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Description
            </label>
            <input
              type="text"
              placeholder="Optional"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Order
            </label>
            <input
              type="number"
              min={0}
              value={order}
              onChange={(e) => setOrder(Number(e.target.value))}
              className="w-full p-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="flex justify-end gap-2 mt-6">
          <Button variant="outline" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={!name.trim() || saving}>
            {saving ? "Creating..." : "Create Section"}
          </Button>
        </div>
      </div>
    </div>
  );
}
