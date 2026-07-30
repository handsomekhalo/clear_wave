// pages/settings/forms/questions.js
// Stripped from dynamic_forms ManageQuestions.js
// Removed: AppLayout, formId prop, questionTypes prop, AssignQuestionToCategoryModal
// Removed: question_type column (ClearWave doesn't use QuestionType model)
// Added: ClearWave SideBar/TopBar, lib/api/forms.js calls
// Kept: table structure, create/edit/status modals pattern — same as your existing code
'use client';

import { useState, useEffect, useCallback } from "react";
import SideBar from "@/components/layout/SideBar";
import TopBar from "@/components/layout/TopBar";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Plus } from "lucide-react";
import { listQuestions } from "../../lib/api/questions";
import { createQuestion } from "../../lib/api/questions";
import { updateQuestion } from "../../lib/api/questions";
import { addQuestionOption } from "../../lib/api/questions";
import { updateQuestionOption } from "../../lib/api/questions";
import { deleteQuestionOption } from "../../lib/api/questions"; 

// import {
//   listQuestions,
//   createQuestion,
//   updateQuestion,
//   addQuestionOption,
//   updateQuestionOption,
//   deleteQuestionOption,
// } from "../../../lib/api/forms";

const INPUT_TYPES = [
  { value: "text", label: "Text" },
  { value: "textarea", label: "Long Text" },
  { value: "number", label: "Number" },
  { value: "date", label: "Date" },
  { value: "email", label: "Email" },
  { value: "select", label: "Dropdown" },
  { value: "checkbox", label: "Checkbox" },
  { value: "yes_no", label: "Yes / No" },
  { value: "file", label: "File Upload" },
];

const INPUT_TYPE_COLORS = {
  text: "bg-gray-100 text-gray-800",
  textarea: "bg-gray-100 text-gray-800",
  number: "bg-blue-100 text-blue-800",
  date: "bg-purple-100 text-purple-800",
  email: "bg-indigo-100 text-indigo-800",
  select: "bg-green-100 text-green-800",
  checkbox: "bg-green-100 text-green-800",
  yes_no: "bg-yellow-100 text-yellow-800",
  file: "bg-orange-100 text-orange-800",
};

const EMPTY_QUESTION = {
  text: "",
  input_type: "text",
  is_required: true,
  allow_other_option: false,
  helper_text: "",
};

export default function QuestionBankPage() {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [collapsed, setCollapsed] = useState(false);

  // Create modal
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createData, setCreateData] = useState(EMPTY_QUESTION);
  const [createOptions, setCreateOptions] = useState([]);
  const [createSaving, setCreateSaving] = useState(false);

  // Edit modal
  const [showEditModal, setShowEditModal] = useState(false);
  const [editData, setEditData] = useState(null);
  const [editOptions, setEditOptions] = useState([]);
  const [editSaving, setEditSaving] = useState(false);

  const fetchQuestions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listQuestions();
      const data = res.data ?? res;
      const questions = Array.isArray(data) ? data : data.questions ?? [];
      setQuestions(
        questions.map((q) => ({
          ...q,
          options: Array.isArray(q.options) ? q.options : [],
        }))
      );
    } catch (err) {
      console.error("Failed to load questions:", err);
      setError("Failed to load questions.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchQuestions();
  }, [fetchQuestions]);

  // ---------------------------------------------------------------------------
  // CREATE
  // ---------------------------------------------------------------------------

  const handleCreate = async () => {
    if (!createData.text.trim()) return;
    setCreateSaving(true);
    try {
      const res = await createQuestion(createData);
      const newId = res.data?.id ?? res.id;

      // Save options if any
      if (
        newId &&
        ["select", "checkbox"].includes(createData.input_type) &&
        createOptions.length > 0
      ) {
        for (let i = 0; i < createOptions.length; i++) {
          if (createOptions[i].text.trim()) {
            await addQuestionOption(newId, {
              text: createOptions[i].text,
              order: i + 1,
            });
          }
        }
      }

      setShowCreateModal(false);
      setCreateData(EMPTY_QUESTION);
      setCreateOptions([]);
      await fetchQuestions();
    } catch (err) {
      console.error("Failed to create question:", err);
      setError("Failed to create question.");
    } finally {
      setCreateSaving(false);
    }
  };

  // ---------------------------------------------------------------------------
  // EDIT
  // ---------------------------------------------------------------------------

  const openEdit = (question) => {
    setEditData({ ...question });
    setEditOptions([...question.options]);
    setShowEditModal(true);
  };

  const handleEdit = async () => {
    if (!editData.text.trim()) return;
    setEditSaving(true);
    try {
      await updateQuestion(editData.id, {
        text: editData.text,
        input_type: editData.input_type,
        is_required: editData.is_required,
        allow_other_option: editData.allow_other_option,
        helper_text: editData.helper_text,
      });
      setShowEditModal(false);
      setEditData(null);
      setEditOptions([]);
      await fetchQuestions();
    } catch (err) {
      console.error("Failed to update question:", err);
      setError("Failed to update question.");
    } finally {
      setEditSaving(false);
    }
  };

  // ---------------------------------------------------------------------------
  // ACTIVATE / DEACTIVATE
  // ---------------------------------------------------------------------------

  const handleToggleActive = async (question) => {
    try {
      await updateQuestion(question.id, { is_active: !question.is_active });
      await fetchQuestions();
    } catch (err) {
      console.error("Failed to toggle question status:", err);
    }
  };

  // ---------------------------------------------------------------------------
  // OPTION HELPERS
  // ---------------------------------------------------------------------------

  const addOption = (list, setList) => {
    setList([...list, { text: "", order: list.length + 1 }]);
  };

  const removeOption = (list, setList, index) => {
    setList(list.filter((_, i) => i !== index));
  };

  const updateOptionText = (list, setList, index, text) => {
    const updated = [...list];
    updated[index] = { ...updated[index], text };
    setList(updated);
  };

  const showOptions = (inputType) =>
    ["select", "checkbox"].includes(inputType);

  // ---------------------------------------------------------------------------
  // RENDER
  // ---------------------------------------------------------------------------

  return (
    <div className="flex">
      <SideBar collapsed={collapsed} setCollapsed={setCollapsed} />
      <main
        className={`flex-1 transition-all duration-300 ${
          collapsed ? "ml-[68px]" : "ml-[240px]"
        }`}
      >
        <TopBar title="Question Bank" />

        <div className="p-6">
          {/* Header */}
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight">
                Question Bank
              </h1>
              <p className="text-sm text-slate-500">
                Your firm's reusable questions. Add them to any form template.
              </p>
            </div>
            <Button onClick={() => setShowCreateModal(true)}>
              <Plus className="mr-2 h-4 w-4" />
              New Question
            </Button>
          </div>

          {loading ? (
            <div className="py-20 text-center text-slate-500">
              Loading questions...
            </div>
          ) : error ? (
            <div className="rounded-md border border-red-200 bg-red-50 p-4 text-red-600">
              {error}
              <button
                onClick={fetchQuestions}
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
                        <th className="px-6 py-3">Question</th>
                        <th className="px-6 py-3">Input Type</th>
                        <th className="px-6 py-3">Required</th>
                        <th className="px-6 py-3">Active</th>
                        <th className="px-6 py-3">Options</th>
                        <th className="px-6 py-3 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200">
                      {questions.length === 0 ? (
                        <tr>
                          <td
                            colSpan={6}
                            className="px-6 py-12 text-center text-slate-400"
                          >
                            No questions yet. Create your first question.
                          </td>
                        </tr>
                      ) : (
                        questions.map((question) => (
                          <tr key={question.id} className="hover:bg-slate-50">
                            <td
                              className="px-6 py-4 font-medium max-w-xs"
                              title={question.text}
                            >
                              {question.text.length > 60
                                ? `${question.text.substring(0, 60)}...`
                                : question.text}
                              {question.helper_text && (
                                <p className="text-xs text-slate-400 mt-0.5">
                                  {question.helper_text}
                                </p>
                              )}
                            </td>
                            <td className="px-6 py-4">
                              <span
                                className={`px-2 py-1 rounded text-xs font-medium ${
                                  INPUT_TYPE_COLORS[question.input_type] ??
                                  "bg-gray-100 text-gray-800"
                                }`}
                              >
                                {question.input_type}
                              </span>
                            </td>
                            <td className="px-6 py-4">
                              <span
                                className={`px-2 py-1 rounded text-xs ${
                                  question.is_required
                                    ? "bg-red-100 text-red-800"
                                    : "bg-gray-100 text-gray-800"
                                }`}
                              >
                                {question.is_required ? "Yes" : "No"}
                              </span>
                            </td>
                            <td className="px-6 py-4">
                              <span
                                className={`px-2 py-1 rounded text-xs ${
                                  question.is_active
                                    ? "bg-green-100 text-green-800"
                                    : "bg-red-100 text-red-800"
                                }`}
                              >
                                {question.is_active ? "Active" : "Inactive"}
                              </span>
                            </td>
                            <td className="px-6 py-4">
                              {question.options.length > 0 ? (
                                <details className="cursor-pointer">
                                  <summary className="text-blue-600 hover:text-blue-800 text-xs">
                                    {question.options.length} options
                                  </summary>
                                  <ul className="list-disc list-inside mt-1 text-xs text-slate-600">
                                    {question.options.map((opt, idx) => (
                                      <li key={idx}>{opt.text}</li>
                                    ))}
                                  </ul>
                                </details>
                              ) : (
                                <span className="text-slate-400 text-xs">—</span>
                              )}
                            </td>
                            <td className="px-6 py-4">
                              <div className="flex justify-end gap-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => openEdit(question)}
                                >
                                  Edit
                                </Button>
                                <Button
                                  variant={
                                    question.is_active ? "destructive" : "outline"
                                  }
                                  size="sm"
                                  onClick={() => handleToggleActive(question)}
                                >
                                  {question.is_active ? "Deactivate" : "Activate"}
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

        {/* ---------------------------------------------------------------- */}
        {/* CREATE QUESTION MODAL                                             */}
        {/* ---------------------------------------------------------------- */}
        {showCreateModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
            <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-lg max-h-[90vh] overflow-y-auto">
              <h3 className="text-lg font-semibold mb-4">New Question</h3>

              <QuestionForm
                data={createData}
                setData={setCreateData}
                options={createOptions}
                setOptions={setCreateOptions}
                addOption={addOption}
                removeOption={removeOption}
                updateOptionText={updateOptionText}
                showOptions={showOptions}
                inputTypes={INPUT_TYPES}
              />

              <div className="flex justify-end gap-2 mt-6">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowCreateModal(false);
                    setCreateData(EMPTY_QUESTION);
                    setCreateOptions([]);
                  }}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleCreate}
                  disabled={!createData.text.trim() || createSaving}
                >
                  {createSaving ? "Saving..." : "Save Question"}
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* ---------------------------------------------------------------- */}
        {/* EDIT QUESTION MODAL                                               */}
        {/* ---------------------------------------------------------------- */}
        {showEditModal && editData && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
            <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-lg max-h-[90vh] overflow-y-auto">
              <h3 className="text-lg font-semibold mb-4">Edit Question</h3>

              <QuestionForm
                data={editData}
                setData={setEditData}
                options={editOptions}
                setOptions={setEditOptions}
                addOption={addOption}
                removeOption={removeOption}
                updateOptionText={updateOptionText}
                showOptions={showOptions}
                inputTypes={INPUT_TYPES}
              />

              <div className="flex justify-end gap-2 mt-6">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowEditModal(false);
                    setEditData(null);
                    setEditOptions([]);
                  }}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleEdit}
                  disabled={!editData.text.trim() || editSaving}
                >
                  {editSaving ? "Saving..." : "Save Changes"}
                </Button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

// ---------------------------------------------------------------------------
// SHARED QUESTION FORM — used in both create and edit modals
// ---------------------------------------------------------------------------

function QuestionForm({
  data,
  setData,
  options,
  setOptions,
  addOption,
  removeOption,
  updateOptionText,
  showOptions,
  inputTypes,
}) {
  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">
          Question Text <span className="text-red-500">*</span>
        </label>
        <textarea
          value={data.text}
          onChange={(e) => setData({ ...data, text: e.target.value })}
          rows={3}
          className="w-full border border-slate-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g. What is your full legal name?"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">
          Input Type <span className="text-red-500">*</span>
        </label>
        <select
          value={data.input_type}
          onChange={(e) =>
            setData({ ...data, input_type: e.target.value })
          }
          className="w-full border border-slate-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {inputTypes.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">
          Helper Text
        </label>
        <input
          type="text"
          value={data.helper_text || ""}
          onChange={(e) => setData({ ...data, helper_text: e.target.value })}
          className="w-full border border-slate-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Optional hint shown below the question"
        />
      </div>

      <div className="flex gap-6">
        <label className="flex items-center gap-2 text-sm text-slate-700">
          <input
            type="checkbox"
            checked={data.is_required}
            onChange={(e) => setData({ ...data, is_required: e.target.checked })}
            className="rounded"
          />
          Required
        </label>

        {showOptions(data.input_type) && (
          <label className="flex items-center gap-2 text-sm text-slate-700">
            <input
              type="checkbox"
              checked={data.allow_other_option}
              onChange={(e) =>
                setData({ ...data, allow_other_option: e.target.checked })
              }
              className="rounded"
            />
            Allow "Other" option
          </label>
        )}
      </div>

      {/* Option builder — only for select and checkbox */}
      {showOptions(data.input_type) && (
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Options
          </label>
          <div className="space-y-2">
            {options.map((opt, idx) => (
              <div key={idx} className="flex gap-2 items-center">
                <input
                  type="text"
                  value={opt.text}
                  onChange={(e) =>
                    updateOptionText(options, setOptions, idx, e.target.value)
                  }
                  className="flex-1 border border-slate-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder={`Option ${idx + 1}`}
                />
                <button
                  type="button"
                  onClick={() => removeOption(options, setOptions, idx)}
                  className="text-red-500 hover:text-red-700 text-xs px-2"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
          <button
            type="button"
            onClick={() => addOption(options, setOptions)}
            className="mt-2 text-sm text-blue-600 hover:text-blue-800 underline"
          >
            + Add Option
          </button>
        </div>
      )}
    </div>
  );
}