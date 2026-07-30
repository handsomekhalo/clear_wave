// components/forms/ManageTemplateModal.js
// Stripped from dynamic_forms FormDetailPage.js
// Removed: AppLayout, useRouter, useParams, Link back to /forms
// Removed: Send Invite button, Open Builder button, Submissions tab
// Removed: AssignCategoryModal (replaced with CreateSectionModal)
// Removed: UpdateFormModal (template edit is handled from FormTemplatesPage)
// Added: ClearWave proxy calls via lib/api/forms.js
// Added: Assign question to section from firm's question bank
// Structure: Modal overlay → Tabs (Sections, Questions preview)

import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Plus, GripVertical, X, Trash2 } from "lucide-react";

// import {
//   getFormTemplate,
//   listFormSections,
//   listSectionQuestions,
//   listQuestions,
//   assignQuestionToSection,
//   removeQuestionFromSection,
// } from "../../lib/api/forms";
import { getFormTemplate } from "../../lib/api/forms";
import { listFormSections } from "../../lib/api/forms";
import { listSectionQuestions } from "../../lib/api/questions";
import { listQuestionOptions } from "../../lib/api/questions";
import { assignQuestionToSection } from "../../lib/api/questions";
import { removeQuestionFromSection } from "../../lib/api/questions";
import CreateSectionModal from "./CreateSectionModal";
import { listQuestions } from "../../lib/api/questions";

export default function ManageTemplateModal({ template, onClose, onUpdate }) {
  const [sections, setSections] = useState([]);
  const [sectionQuestions, setSectionQuestions] = useState({}); // { sectionId: [questions] }
  const [questionBank, setQuestionBank] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Section modal
  const [showSectionModal, setShowSectionModal] = useState(false);

  // Assign question state
  const [assigningToSection, setAssigningToSection] = useState(null); // section object
  const [selectedQuestionId, setSelectedQuestionId] = useState("");
  const [assigning, setAssigning] = useState(false);
  const [assignError, setAssignError] = useState(null);

  // ---------------------------------------------------------------------------
  // FETCH
  // ---------------------------------------------------------------------------

  const fetchSections = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listFormSections(template.id);
      const data = res.data ?? res;
      const sectionsData = Array.isArray(data) ? data : [];
      setSections(sectionsData);

      // Fetch questions for each section
      const questionsMap = {};
      for (const section of sectionsData) {
        try {
          const sqRes = await listSectionQuestions(template.id, section.id);
          const sqData = sqRes.data ?? sqRes;
          questionsMap[section.id] = Array.isArray(sqData) ? sqData : [];
        } catch {
          questionsMap[section.id] = [];
        }
      }
      setSectionQuestions(questionsMap);
    } catch (err) {
      console.error("Failed to load sections:", err);
      setError("Failed to load sections.");
    } finally {
      setLoading(false);
    }
  }, [template.id]);

  const fetchQuestionBank = useCallback(async () => {
    try {
      const res = await listQuestions();
      const data = res.data ?? res;
      setQuestionBank(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load question bank:", err);
    }
  }, []);

  useEffect(() => {
    fetchSections();
    fetchQuestionBank();
  }, [fetchSections, fetchQuestionBank]);

  // ---------------------------------------------------------------------------
  // ASSIGN QUESTION TO SECTION
  // ---------------------------------------------------------------------------

  const handleAssignQuestion = async (section) => {
    if (!selectedQuestionId) {
      setAssignError("Please select a question.");
      return;
    }

    setAssigning(true);
    setAssignError(null);

    try {
      await assignQuestionToSection(template.id, section.id, {
        question: Number(selectedQuestionId),
        order: (sectionQuestions[section.id]?.length ?? 0) + 1,
      });

      setAssigningToSection(null);
      setSelectedQuestionId("");
      await fetchSections();
    } catch (err) {
      console.error("Failed to assign question:", err);
      setAssignError(
        err?.response?.data?.non_field_errors?.[0] ||
        err?.response?.data?.detail ||
        "Failed to assign question."
      );
    } finally {
      setAssigning(false);
    }
  };

  // ---------------------------------------------------------------------------
  // REMOVE QUESTION FROM SECTION
  // ---------------------------------------------------------------------------

  const handleRemoveQuestion = async (section, sqId) => {
    if (!confirm("Remove this question from the section?")) return;
    try {
      await removeQuestionFromSection(template.id, section.id, sqId);
      await fetchSections();
    } catch (err) {
      console.error("Failed to remove question:", err);
    }
  };

  // ---------------------------------------------------------------------------
  // TOTAL QUESTIONS COUNT
  // ---------------------------------------------------------------------------

  const totalQuestions = Object.values(sectionQuestions).reduce(
    (total, qs) => total + qs.length,
    0
  );

  // Questions already assigned to this section (to filter from dropdown)
  const assignedQuestionIds = (sectionId) =>
    new Set(
      (sectionQuestions[sectionId] ?? []).map((sq) => sq.question?.id)
    );

  // ---------------------------------------------------------------------------
  // RENDER
  // ---------------------------------------------------------------------------

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <div>
            <h2 className="text-xl font-semibold">{template.name}</h2>
            <p className="text-sm text-slate-500 mt-0.5">
              {sections.length} sections · {totalQuestions} questions
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-700"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {loading ? (
            <div className="py-20 text-center text-slate-500">
              Loading template...
            </div>
          ) : error ? (
            <div className="rounded-md border border-red-200 bg-red-50 p-4 text-red-600">
              {error}
            </div>
          ) : (
            <Tabs defaultValue="sections">
              <TabsList>
                <TabsTrigger value="sections">Sections</TabsTrigger>
                <TabsTrigger value="questions">Questions Preview</TabsTrigger>
              </TabsList>

              {/* ---------------------------------------------------------- */}
              {/* SECTIONS TAB                                                 */}
              {/* ---------------------------------------------------------- */}
              <TabsContent value="sections" className="mt-4">
                <Card>
                  <CardContent className="p-0">

                    {/* Section list header */}
                    <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
                      <p className="text-sm text-slate-500">
                        {sections.length} sections · click to expand
                      </p>
                      <Button
                        size="sm"
                        onClick={() => setShowSectionModal(true)}
                      >
                        <Plus className="mr-1.5 h-3.5 w-3.5" />
                        Add Section
                      </Button>
                    </div>

                    {sections.length === 0 ? (
                      <div className="px-6 py-8 text-sm text-slate-500">
                        No sections yet. Add your first section.
                      </div>
                    ) : (
                      <div className="px-6">
                        <Accordion type="multiple" className="w-full">
                          {sections.map((section) => (
                            <AccordionItem
                              key={section.id}
                              value={String(section.id)}
                            >
                              <AccordionTrigger>
                                <div className="text-left">
                                  <p className="font-medium">{section.name}</p>
                                  <p className="text-xs text-slate-500">
                                    {sectionQuestions[section.id]?.length ?? 0} questions
                                    {section.description && ` · ${section.description}`}
                                  </p>
                                </div>
                              </AccordionTrigger>

                              <AccordionContent>
                                {/* Questions in this section */}
                                {!sectionQuestions[section.id]?.length ? (
                                  <p className="pb-3 text-sm text-slate-400">
                                    No questions assigned yet.
                                  </p>
                                ) : (
                                  <ul className="space-y-2 pb-3">
                                    {sectionQuestions[section.id].map(
                                      (sq, index) => (
                                        <li
                                          key={sq.id}
                                          className="flex items-center justify-between rounded-md border border-slate-200 bg-slate-50 px-3 py-2"
                                        >
                                          <div className="flex items-center gap-3">
                                            <GripVertical className="h-4 w-4 text-slate-400" />
                                            <span className="text-xs text-slate-500">
                                              {index + 1}.
                                            </span>
                                            <span className="text-sm font-medium">
                                              {sq.question?.text}
                                            </span>
                                            <span className="text-xs text-slate-400">
                                              · {sq.question?.input_type}
                                            </span>
                                            {sq.is_required && (
                                              <span className="rounded bg-red-50 px-1.5 py-0.5 text-[10px] font-medium text-red-700">
                                                Required
                                              </span>
                                            )}
                                          </div>
                                          <button
                                            onClick={() =>
                                              handleRemoveQuestion(section, sq.id)
                                            }
                                            className="text-slate-400 hover:text-red-500 ml-2"
                                          >
                                            <Trash2 className="h-3.5 w-3.5" />
                                          </button>
                                        </li>
                                      )
                                    )}
                                  </ul>
                                )}

                                {/* Assign question inline */}
                                {assigningToSection?.id === section.id ? (
                                  <div className="mt-2 flex items-center gap-2">
                                    <select
                                      value={selectedQuestionId}
                                      onChange={(e) =>
                                        setSelectedQuestionId(e.target.value)
                                      }
                                      className="flex-1 border border-slate-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    >
                                      <option value="">
                                        Select a question...
                                      </option>
                                      {questionBank
                                        .filter(
                                          (q) =>
                                            q.is_active &&
                                            !assignedQuestionIds(section.id).has(q.id)
                                        )
                                        .map((q) => (
                                          <option key={q.id} value={q.id}>
                                            {q.text.length > 60
                                              ? `${q.text.substring(0, 60)}...`
                                              : q.text}{" "}
                                            [{q.input_type}]
                                          </option>
                                        ))}
                                    </select>
                                    {assignError && (
                                      <span className="text-xs text-red-600">
                                        {assignError}
                                      </span>
                                    )}
                                    <Button
                                      size="sm"
                                      onClick={() =>
                                        handleAssignQuestion(section)
                                      }
                                      disabled={
                                        !selectedQuestionId || assigning
                                      }
                                    >
                                      {assigning ? "Adding..." : "Add"}
                                    </Button>
                                    <Button
                                      size="sm"
                                      variant="outline"
                                      onClick={() => {
                                        setAssigningToSection(null);
                                        setSelectedQuestionId("");
                                        setAssignError(null);
                                      }}
                                    >
                                      Cancel
                                    </Button>
                                  </div>
                                ) : (
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    className="mt-1"
                                    onClick={() => {
                                      setAssigningToSection(section);
                                      setSelectedQuestionId("");
                                      setAssignError(null);
                                    }}
                                  >
                                    <Plus className="mr-1.5 h-3.5 w-3.5" />
                                    Assign Question
                                  </Button>
                                )}
                              </AccordionContent>
                            </AccordionItem>
                          ))}
                        </Accordion>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              {/* ---------------------------------------------------------- */}
              {/* QUESTIONS PREVIEW TAB                                        */}
              {/* Mirrors FormDetailPage Questions tab exactly                 */}
              {/* ---------------------------------------------------------- */}
              <TabsContent value="questions" className="mt-4">
                <div className="space-y-4">
                  {sections.length === 0 ? (
                    <p className="text-sm text-slate-400 py-8 text-center">
                      No sections yet.
                    </p>
                  ) : (
                    sections.map((section) => (
                      <Card key={section.id}>
                        <CardContent className="p-0">
                          <div className="border-b border-slate-200 px-6 py-3">
                            <p className="text-xs uppercase tracking-wide text-slate-500">
                              {section.name}
                            </p>
                          </div>

                          {!sectionQuestions[section.id]?.length ? (
                            <div className="px-6 py-4 text-sm text-slate-400">
                              No questions assigned.
                            </div>
                          ) : (
                            <ul className="divide-y divide-slate-200">
                              {sectionQuestions[section.id].map((sq) => (
                                <li key={sq.id} className="px-6 py-4">
                                  <div className="space-y-1">
                                    <div className="flex items-center gap-2">
                                      <p className="font-medium text-sm">
                                        {sq.question?.text}
                                      </p>
                                      {sq.is_required && (
                                        <span className="rounded bg-red-50 px-1.5 py-0.5 text-[10px] font-medium text-red-700">
                                          Required
                                        </span>
                                      )}
                                    </div>
                                    <p className="text-xs text-slate-500">
                                      Type: {sq.question?.input_type}
                                    </p>
                                    {sq.question?.helper_text && (
                                      <p className="text-xs text-slate-400 italic">
                                        {sq.question.helper_text}
                                      </p>
                                    )}
                                    {/* Options preview for select/checkbox */}
                                    {sq.question?.options?.length > 0 && (
                                      <div className="flex flex-wrap gap-1 mt-1">
                                        {sq.question.options.map((opt) => (
                                          <span
                                            key={opt.id}
                                            className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-600"
                                          >
                                            {opt.text}
                                          </span>
                                        ))}
                                      </div>
                                    )}
                                  </div>
                                </li>
                              ))}
                            </ul>
                          )}
                        </CardContent>
                      </Card>
                    ))
                  )}
                </div>
              </TabsContent>
            </Tabs>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-200 flex justify-end">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>

      {/* Create Section Modal */}
      {showSectionModal && (
        <CreateSectionModal
          templateId={template.id}
          onClose={() => setShowSectionModal(false)}
          onSuccess={fetchSections}
        />
      )}
    </div>
  );
}