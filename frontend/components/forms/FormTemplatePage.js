// pages/settings/forms/index.js  (or wherever settings/forms lives in your ClearWave routing)
// Stripped from dynamic_forms FormsPage.js
// Removed: AppLayout, invite button, Link to /forms/:id (replaced with manage modal)
// Added: ClearWave SideBar/TopBar, lib/api/forms.js calls, template-specific fields
'use client';

import { useState, useEffect, useCallback } from "react";
import SideBar from "@/components/layout/SideBar";
import TopBar from "@/components/layout/TopBar";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Plus } from "lucide-react";
// import {
//   listFormTemplates,
//   createFormTemplate,
//   updateFormTemplate,
// } from "../../../lib/api/forms";
import { listFormTemplates } from "../../lib/api/forms";
import { createFormTemplate } from "../../lib/api/forms";
import { updateFormTemplate } from "../../lib/api/forms";

// Modals — you will build these same as your existing ClearWave modals
import CreateSectionModal from "@/components/forms/CreateSectionModal"; 
import ManageTemplateModal from "./Managetemplatemodal ";

export default function FormTemplatesPage() {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [collapsed, setCollapsed] = useState(false);

  // Create modal state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createData, setCreateData] = useState({
    name: "",
    description: "",
    case_type: null,
    is_active: true,
  });

  // Manage/edit modal state    
  const [showManageModal, setShowManageModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  const fetchTemplates = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listFormTemplates();
      const data = res.data ?? res;
      setTemplates(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load templates:", err);
      setError("Failed to load form templates.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTemplates();
  }, [fetchTemplates]);

  const handleCreate = async () => {
    try {
      await createFormTemplate(createData);
      setShowCreateModal(false);
      setCreateData({ name: "", description: "", case_type: null, is_active: true });
      await fetchTemplates();
    } catch (err) {
      console.error("Failed to create template:", err);
      setError("Failed to create template.");
    }
  };

  const handleToggleActive = async (template) => {
    try {
      await updateFormTemplate(template.id, { is_active: !template.is_active });
      await fetchTemplates();
    } catch (err) {
      console.error("Failed to update template:", err);
    }
  };

  const handleManage = (template) => {
    setSelectedTemplate(template);
    setShowManageModal(true);
  };

  return (
    <div className="flex">
      <SideBar collapsed={collapsed} setCollapsed={setCollapsed} />
      <main
        className={`flex-1 transition-all duration-300 ${
          collapsed ? "ml-[68px]" : "ml-[240px]"
        }`}
      >
        <TopBar title="Form Templates" />

        <div className="p-6">
          {/* Header */}
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight">
                Form Templates
              </h1>
              <p className="text-sm text-slate-500">
                Build reusable intake forms for your matter types.
              </p>
            </div>
            <Button onClick={() => setShowCreateModal(true)}>
              <Plus className="mr-2 h-4 w-4" />
              New Template
            </Button>
          </div>

          {/* Loading */}
          {loading ? (
            <div className="py-20 text-center text-slate-500">
              Loading templates...
            </div>
          ) : error ? (
            <div className="rounded-md border border-red-200 bg-red-50 p-4 text-red-600">
              {error}
              <button
                onClick={fetchTemplates}
                className="ml-3 text-sm underline text-blue-600"
              >
                Try again
              </button>
            </div>
          ) : (
            <Card className="border-slate-200 shadow-sm">
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="border-b border-slate-200 text-left text-xs uppercase tracking-wide text-slate-500">
                      <tr>
                        <th className="px-6 py-3">Template Name</th>
                        <th className="px-6 py-3">Description</th>
                        <th className="px-6 py-3">Matter Type</th>
                        <th className="px-6 py-3">Sections</th>
                        <th className="px-6 py-3">Status</th>
                        <th className="px-6 py-3 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200">
                      {templates.length === 0 ? (
                        <tr>
                          <td
                            colSpan={6}
                            className="px-6 py-12 text-center text-slate-400"
                          >
                            No templates yet. Create your first one.
                          </td>
                        </tr>
                      ) : (
                        templates.map((template) => (
                          <tr key={template.id} className="hover:bg-slate-50">
                            <td className="px-6 py-4 font-medium">
                              {template.name}
                            </td>
                            <td className="px-6 py-4 text-slate-500">
                              {template.description || "—"}
                            </td>
                            <td className="px-6 py-4 text-slate-500">
                              {template.case_type?.name || "—"}
                            </td>
                            <td className="px-6 py-4 text-slate-500">
                              {template.section_count ?? "—"}
                            </td>
                            <td className="px-6 py-4">
                              <span
                                className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
                                  template.is_active
                                    ? "bg-green-100 text-green-700"
                                    : "bg-slate-100 text-slate-600"
                                }`}
                              >
                                {template.is_active ? "Active" : "Inactive"}
                              </span>
                            </td>
                            <td className="px-6 py-4">
                              <div className="flex justify-end gap-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleManage(template)}
                                >
                                  Manage
                                </Button>
                                <Button
                                  variant={template.is_active ? "destructive" : "outline"}
                                  size="sm"
                                  onClick={() => handleToggleActive(template)}
                                >
                                  {template.is_active ? "Deactivate" : "Activate"}
                                </Button>
                              </div>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Create Template Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
            <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-lg">
              <h3 className="text-lg font-semibold mb-4">New Form Template</h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Template Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={createData.name}
                    onChange={(e) =>
                      setCreateData({ ...createData, name: e.target.value })
                    }
                    className="w-full border border-slate-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g. Conveyancing Intake"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={createData.description}
                    onChange={(e) =>
                      setCreateData({ ...createData, description: e.target.value })
                    }
                    rows={3}
                    className="w-full border border-slate-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Optional description"
                  />
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={createData.is_active}
                    onChange={(e) =>
                      setCreateData({ ...createData, is_active: e.target.checked })
                    }
                    className="rounded"
                  />
                  <label htmlFor="is_active" className="text-sm text-slate-700">
                    Active
                  </label>
                </div>
              </div>

              <div className="flex justify-end gap-2 mt-6">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowCreateModal(false);
                    setCreateData({ name: "", description: "", case_type: null, is_active: true });
                  }}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleCreate}
                  disabled={!createData.name.trim()}
                >
                  Create Template
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Manage Template Modal — sections + questions live here */}
        {showManageModal && selectedTemplate && (
          <ManageTemplateModal
            template={selectedTemplate}
            onClose={() => {
              setShowManageModal(false);
              setSelectedTemplate(null);
            }}
            onUpdate={fetchTemplates}
          />
        )}
      </main>
    </div>
  );
}