"use client";
import { createPortal } from "react-dom";
import { useState, useEffect } from "react";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DocumentsList } from "./DocumentsList";
import { UploadDocumentModal } from "./UploadDocumentModal";
import {
  getCaseDetails, getCaseNotes, addNote, updateCase,
  assignToCase, getFirmMembers, getAllMatterTypes,
} from "@/lib/api/cases";

import { listFormTemplates } from "../../lib/api/forms";
import {listCaseFormAssignments} from "../../lib/api/questions"; 
import {assignFormToCase} from "../../lib/api/questions";
import {reviewCaseFormAssignment} from "../../lib/api/questions";
import { getFormSubmission } from "../../lib/api/submissions";
import { listFormResponses } from "../../lib/api/submissions";
import backendApi from "../../lib/backendApi";
import { addTimeLog, listTimeLogs, deleteTimeLog } from "@/lib/api/cases"

import {
  Accordion, AccordionContent, AccordionItem, AccordionTrigger,
} from "@/components/ui/accordion";
import { Plus, Clock, CheckCircle, XCircle, AlertCircle } from "lucide-react";

// ── helpers ────────────────────────────────────────────────────────────────

function parseDeadline(deadline) {
  if (!deadline) return "";
  if (typeof deadline === "string" && deadline.includes("T")) return deadline.split("T")[0];
  if (typeof deadline === "string" && /^\d{4}-\d{2}-\d{2}$/.test(deadline)) return deadline;
  try { return new Date(deadline).toISOString().split("T")[0]; } catch { return ""; }
}

function formatDeadlineDisplay(deadline) {
  const parsed = parseDeadline(deadline);
  if (!parsed) return "—";
  try {
    return new Date(parsed + "T00:00:00").toLocaleDateString("en-ZA", {
      year: "numeric", month: "long", day: "numeric",
    });
  } catch { return parsed; }
}

const STATUS_OPTIONS = [
  { value: "new",     label: "New" },
  { value: "active",  label: "Active" },
  { value: "pending", label: "Pending" },
  { value: "closed",  label: "Closed" },
];

// assignment status → pill style
const FORM_STATUS_STYLES = {
  pending:      "bg-gray-100 text-gray-600",
  in_progress:  "bg-blue-100 text-blue-700",
  submitted:    "bg-yellow-100 text-yellow-700",
  under_review: "bg-orange-100 text-orange-700",
  approved:     "bg-green-100 text-green-700",
  rejected:     "bg-red-100 text-red-700",
};

// ── main component ─────────────────────────────────────────────────────────

export function ViewCaseModal({ open, onOpenChange, caseId, onUpdate }) {
  const [caseData, setCaseData]         = useState(null);
  const [loading, setLoading]           = useState(false);
  const [isEditing, setIsEditing]       = useState(false);
  const [savingCase, setSavingCase]     = useState(false);
  const [saveError, setSaveError]       = useState(null);

  const [notes, setNotes]               = useState([]);
  const [noteInput, setNoteInput]       = useState("");
  const [notesLoading, setNotesLoading] = useState(false);
  const [addingNote, setAddingNote]     = useState(false);

  const [form, setForm] = useState({
    title: "", description: "", status: "", priority: "",
    matter_type: "", deadline: "",
  });

  const [members, setMembers]         = useState([]);
  const [matterTypes, setMatterTypes] = useState([]);
  const [selectedUser, setSelectedUser] = useState("");
  const [showUploadModal, setShowUploadModal] = useState(false);

  // ── forms tab state ──────────────────────────────────────────────────────
  const [assignments, setAssignments]         = useState([]);
  const [assignmentsLoading, setAssignmentsLoading] = useState(false);
  const [templates, setTemplates]             = useState([]);

  // assign form modal
  const [showAssignForm, setShowAssignForm]   = useState(false);
  const [assignTemplateId, setAssignTemplateId] = useState("");
  const [assignDueDate, setAssignDueDate]     = useState("");
  const [assigning, setAssigning]             = useState(false);
  const [assignError, setAssignError]         = useState(null);

  // review drawer
  const [reviewingAssignment, setReviewingAssignment] = useState(null);
  const [submission, setSubmission]           = useState(null);
  const [responses, setResponses]             = useState([]);
  const [reviewLoading, setReviewLoading]     = useState(false);
  const [reviewNotes, setReviewNotes]         = useState("");
  const [submitting, setSubmitting]           = useState(false);
  const [reviewError, setReviewError]         = useState(null);

  //time logging
  
    const [timeLogs, setTimeLogs]         = useState([])
    const [timeLogsLoading, setTimeLogsLoading] = useState(false)
    const [showTimeForm, setShowTimeForm] = useState(false)
    const [timeForm, setTimeForm]         = useState({
      date: new Date().toISOString().split("T")[0],
      duration: "",
      activity_type: "other",
      description: "",
      is_billable: true,
    })
  const [savingTime, setSavingTime]     = useState(false)
  const [timeError, setTimeError]       = useState(null)

  // ── Messages state ────────────────────────────────────────────────────────

  const [messages, setMessages]     = useState([])
  const [messageInput, setMessageInput] = useState("")
  const [sendingMessage, setSendingMessage] = useState(false)
  const [messagesLoading, setMessagesLoading] = useState(false)

  // ── data fetchers ────────────────────────────────────────────────────────

  const fetchCase = async () => {
    setLoading(true);
    try {
      const res = await getCaseDetails(caseId);
      setCaseData(res.data || res);
    } catch (err) { console.error("Failed to load case", err); }
    finally { setLoading(false); }
  };

  const fetchNotes = async () => {
    setNotesLoading(true);
    try {
      const res = await getCaseNotes(caseId);
      const data = res.data || res;
      setNotes(Array.isArray(data) ? data : []);
    } catch (err) { console.error("Failed to load notes", err); }
    finally { setNotesLoading(false); }
  };

  const fetchMembers = async () => {
    try {
      const res = await getFirmMembers();
      setMembers(Array.isArray(res) ? res : res.data || []);
    } catch (err) { console.error("Failed to load members", err); }
  };

  const fetchMatterTypes = async () => {
    try {
      const res = await getAllMatterTypes();
      setMatterTypes(Array.isArray(res) ? res : res.data || []);
    } catch (err) { console.error("Failed to load matter types", err); }
  };

  const fetchAssignments = async () => {
    setAssignmentsLoading(true);
    try {
      const res = await listCaseFormAssignments(caseId);
      const data = res.data ?? res;
      setAssignments(Array.isArray(data) ? data : []);
    } catch (err) { console.error("Failed to load assignments", err); }
    finally { setAssignmentsLoading(false); }
  };

  const fetchTemplates = async () => {
    try {
      const res = await listFormTemplates();
      const data = res.data ?? res;
      setTemplates(Array.isArray(data) ? data.filter(t => t.is_active) : []);
    } catch (err) { console.error("Failed to load templates", err); }
  };

  const fetchMessages = async () => {
  setMessagesLoading(true)
  try {
    const res = await backendApi.get(
      `/client_management/list_case_messages/${caseId}/`
    )
    const data = res.data?.data ?? res.data
    setMessages(Array.isArray(data) ? data : [])
  } catch (err) {
    console.error("Failed to load messages", err)
  } finally {
    setMessagesLoading(false)
  }
}

const fetchTimeLogs = async () => {
  setTimeLogsLoading(true)
  try {
    const res = await listTimeLogs(caseId)
    const data = res?.data ?? res
    setTimeLogs(Array.isArray(data) ? data : [])
  } catch (err) {
    console.error("Failed to load time logs", err)
  } finally {
    setTimeLogsLoading(false)
  }
}

  // ── effects ──────────────────────────────────────────────────────────────

  useEffect(() => {
    if (open) {
      fetchMembers();
      fetchMatterTypes();
      fetchTemplates();
      if (caseId) { 
        fetchCase(); 
        fetchNotes(); 
        fetchAssignments();
        fetchMessages();
         fetchTimeLogs()
 }
    }
    if (!open) {
      setIsEditing(false);
      setSaveError(null);
      setShowAssignForm(false);
      setReviewingAssignment(null);
      setSubmission(null);
      setResponses([]);
      setSelectedUser("");
      setShowTimeForm(false)
      setTimeError(null)
    }
    
  }, [open, caseId]);

  useEffect(() => {
    if (caseData) {
      setForm({
        title:       caseData.title || "",
        description: caseData.description || "",
        status:      caseData.status || "",
        priority:    caseData.priority || "",
        matter_type: caseData.matter_type?.id?.toString() || "",
        deadline:    parseDeadline(caseData.deadline),
      });
    }
  }, [caseData]);


  useEffect(() => {
  if (caseData?.assigned_lawyer) {
    setSelectedUser(caseData.assigned_lawyer.id?.toString() || "");
  } else {
    setSelectedUser(""); // ← reset when no lawyer assigned
  }
}, [caseData]);

  // useEffect(() => {
  //   if (caseData?.assigned_lawyer) {
  //     setSelectedUser(caseData.assigned_lawyer.id?.toString() || "");
  //   }
  // }, [caseData]);

  const set = (key, value) => setForm(prev => ({ ...prev, [key]: value }));

  
  // ── case save ────────────────────────────────────────────────────────────

  const handleSave = async () => {
    setSavingCase(true);
    setSaveError(null);
    try {
      const payload = {
        title: form.title, description: form.description,
        status: form.status, priority: form.priority,
        deadline: form.deadline || null,
      };
      if (form.matter_type) payload.matter_type = Number(form.matter_type);
      await updateCase(caseId, payload);
      if (selectedUser) await assignToCase(caseId, { user_id: Number(selectedUser) });
      setIsEditing(false);
      await fetchCase();
      onUpdate?.();
    } catch (err) {
      console.error("Update failed", err);
      setSaveError("Failed to save changes. Please try again.");
    } finally { setSavingCase(false); }
  };

  // ── notes ────────────────────────────────────────────────────────────────

  const handleAddNote = async () => {
    if (!noteInput.trim()) return;
    setAddingNote(true);
    try {
      await addNote(caseId, { content: noteInput, is_pinned: false });
      setNoteInput("");
      await fetchNotes();
    } catch (err) { console.error("Failed to add note", err); }
    finally { setAddingNote(false); }
  };

  const handleSendMessage = async () => {
  if (!messageInput.trim()) return
  setSendingMessage(true)
  try {
    await backendApi.post(
      `/client_management/send_case_message/${caseId}/`,
      { content: messageInput }
    )
    setMessageInput("")
    await fetchMessages()
  } catch (err) {
    console.error("Failed to send message", err)
  } finally {
    setSendingMessage(false)
  }
}

//submit time log hndler 

const handleAddTimeLog = async () => {
  if (!timeForm.duration || !timeForm.description || !timeForm.date) {
    setTimeError("Date, duration and description are required.")
    return
  }
  setSavingTime(true)
  setTimeError(null)
  try {
    await addTimeLog(caseId, timeForm)
    setShowTimeForm(false)
    setTimeForm({
      date: new Date().toISOString().split("T")[0],
      duration: "",
      activity_type: "other",
      description: "",
      is_billable: true,
    })
    await fetchTimeLogs()
  } catch (err) {
    console.error("Failed to add time log", err)
    setTimeError("Failed to save time log. Please try again.")
  } finally {
    setSavingTime(false)
  }
}

const handleDeleteTimeLog = async (logId) => {
  if (!confirm("Delete this time entry?")) return
  try {
    await deleteTimeLog(caseId, logId)
    await fetchTimeLogs()
  } catch (err) {
    console.error("Failed to delete time log", err)
  }
}

  // ── assign form to case ──────────────────────────────────────────────────

  const handleAssignForm = async () => {
    if (!assignTemplateId) {
      setAssignError("Please select a template.");
      return;
    }
    setAssigning(true);
    setAssignError(null);
    try {
      await assignFormToCase(caseId, {
        template: Number(assignTemplateId),
        due_date: assignDueDate || undefined,
      });
      setShowAssignForm(false);
      setAssignTemplateId("");
      setAssignDueDate("");
      await fetchAssignments();
    } catch (err) {
      console.error("Failed to assign form", err);
      setAssignError(
        err?.response?.data?.non_field_errors?.[0] ||
        err?.response?.data?.template?.[0] ||
        "Failed to assign form."
      );
    } finally { setAssigning(false); }
  };

  // ── open review drawer ───────────────────────────────────────────────────

  const handleOpenReview = async (assignment) => {
    setReviewingAssignment(assignment);
    setReviewNotes(assignment.review_notes || "");
    setReviewError(null);
    setReviewLoading(true);
    setSubmission(null);
    setResponses([]);

    try {
      const subRes = await getFormSubmission(assignment.id);
      const subData = subRes.data ?? subRes;
      setSubmission(subData);

      if (subData?.id) {
        const respRes = await listFormResponses(subData.id);
        const respData = respRes.data ?? respRes;
        setResponses(Array.isArray(respData) ? respData : []);
      }
    } catch (err) {
      console.error("Failed to load submission", err);
      setReviewError("Could not load submission. The client may not have started yet.");
    } finally { setReviewLoading(false); }
  };

  // ── review approve / reject ──────────────────────────────────────────────

  const handleReview = async (status) => {
    if (!reviewingAssignment) return;
    setSubmitting(true);
    setReviewError(null);
    try {
      await reviewCaseFormAssignment(caseId, reviewingAssignment.id, {
        status,
        review_notes: reviewNotes,
      });
      setReviewingAssignment(null);
      await fetchAssignments();
    } catch (err) {
      console.error("Failed to review", err);
      setReviewError(
        err?.response?.data?.error ||
        err?.response?.data?.detail ||
        "Failed to submit review."
      );
    } finally { setSubmitting(false); }
  };

  // ── group responses by section ───────────────────────────────────────────

  const responsesBySection = () => {
    const map = {};
    for (const r of responses) {
      const key = r.section?.id ?? "unsectioned";
      const label = r.section ? `${r.section.name ?? "Section"}` : "General";
      if (!map[key]) map[key] = { label, responses: [] };
      map[key].responses.push(r);
    }
    return Object.values(map);
  };

  // ── answer display helper ────────────────────────────────────────────────

  const renderAnswer = (r) => {
    if (r.response_text)    return r.response_text;
    if (r.response_date)    return r.response_date;
    if (r.response_number !== null && r.response_number !== undefined)
                            return String(r.response_number);
    if (r.response_boolean !== null && r.response_boolean !== undefined)
                            return r.response_boolean ? "Yes" : "No";
    if (r.selected_option)  return r.selected_option.text;
    if (r.document)         return `📎 ${r.document.name}`;
    if (r.other_text)       return `Other: ${r.other_text}`;
    return <span className="text-slate-400 italic">— not answered</span>;
  };

  if (!caseId) return null;

  // ── render ───────────────────────────────────────────────────────────────




  return (
  <>
    <Dialog open={open} onOpenChange={onOpenChange}>
             <DialogContent className="sm:max-w-[900px] max-h-[90vh] overflow-y-auto">
        <DialogHeader className="flex flex-row justify-between items-center">
          <DialogTitle className="text-lg font-semibold">
            {loading ? "Loading..." : caseData?.title || "Case Details"}
          </DialogTitle>
          <div className="flex gap-2">
            {isEditing ? (
              <>
                <Button variant="outline" size="sm"
                  onClick={() => { setIsEditing(false); setSaveError(null); }}>
                  Cancel
                </Button>
                <Button size="sm" onClick={handleSave} disabled={savingCase}>
                  {savingCase ? "Saving..." : "Save Changes"}
                </Button>
              </>
            ) : (
              <Button size="sm" onClick={() => setIsEditing(true)}>Edit</Button>
            )}
          </div>
        </DialogHeader>

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="flex flex-col items-center gap-3 text-gray-400">
              <svg className="animate-spin h-8 w-8" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
              </svg>
              <span className="text-sm">Loading case details...</span>
            </div>
          </div>
        ) : (
          <Tabs defaultValue="details">
            <TabsList className="mb-4">
            <TabsTrigger value="details">Details</TabsTrigger>
            <TabsTrigger value="notes">Notes ({notes.length})</TabsTrigger>
            <TabsTrigger value="documents">Documents</TabsTrigger>
            <TabsTrigger value="forms">
              Forms {assignments.length > 0 && `(${assignments.length})`}
            </TabsTrigger>
            <TabsTrigger value="messages">Messages</TabsTrigger>
            <TabsTrigger value="time">
  Time {timeLogs.length > 0 && `(${timeLogs.length})`}
</TabsTrigger>
          </TabsList>

            {/* ── DETAILS TAB ── */}
            <TabsContent value="details" className="space-y-4">
              {saveError && (
                <p className="text-sm text-red-500 bg-red-50 px-3 py-2 rounded">{saveError}</p>
              )}
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2 space-y-1">
                  <Label>Case Title</Label>
                  {isEditing
                    ? <Input value={form.title} onChange={e => set("title", e.target.value)} />
                    : <p className="text-sm font-medium">{caseData?.title || "—"}</p>}
                </div>

                <div className="space-y-1">
                  <Label>Status</Label>
                  {isEditing ? (
                    <Select value={form.status} onValueChange={v => set("status", v)}>
                      <SelectTrigger><SelectValue placeholder="Select status" /></SelectTrigger>
                      <SelectContent>
                        {STATUS_OPTIONS.map(s => (
                          <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <span className={`inline-block text-xs px-2 py-1 rounded-full font-medium capitalize ${
                      caseData?.status === "active"  ? "bg-green-100 text-green-700"  :
                      caseData?.status === "pending" ? "bg-yellow-100 text-yellow-700":
                      caseData?.status === "closed"  ? "bg-gray-100 text-gray-500"    :
                      "bg-blue-100 text-blue-600"
                    }`}>
                      {caseData?.status || "—"}
                    </span>
                  )}
                </div>

                <div className="space-y-1">
                  <Label>Deadline</Label>
                  {isEditing
                    ? <Input type="date" value={form.deadline} onChange={e => set("deadline", e.target.value)} />
                    : <p className="text-sm">{formatDeadlineDisplay(caseData?.deadline)}</p>}
                </div>

                <div className="space-y-1">
                  <Label>Matter Type</Label>
                  {isEditing ? (
                    <Select value={form.matter_type} onValueChange={v => set("matter_type", v)}>
                      <SelectTrigger><SelectValue placeholder="Select matter type" /></SelectTrigger>
                      <SelectContent>
                        {matterTypes.map(mt => (
                          <SelectItem key={String(mt.id ?? mt.name)} value={String(mt.id)}>
                            {mt.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <p className="text-sm">{caseData?.matter_type?.name || "—"}</p>
                  )}
                </div>

                <div className="space-y-1">
                  <Label>Assigned Lawyer</Label>
                  {isEditing ? (
                    <Select value={selectedUser} onValueChange={setSelectedUser}>
                      <SelectTrigger><SelectValue placeholder="Assign a lawyer" /></SelectTrigger>
                      <SelectContent>
                        {members.filter(m => m.role === "lawyer").map(m => (
                          <SelectItem key={String(m.id)} value={String(m.id)}>{m.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <p className="text-sm">
                      {caseData?.assigned_lawyer
                        ? (caseData.assigned_lawyer.name ||
                           `${caseData.assigned_lawyer.first_name || ""} ${caseData.assigned_lawyer.last_name || ""}`.trim() ||
                           "Unassigned")
                        : "Unassigned"}
                    </p>
                  )}
                </div>

                <div className="space-y-1">
                  <Label>Client</Label>
                  <p className="text-sm">
                    {caseData?.client
                      ? (caseData.client.name || `${caseData.client.first_name || ""} ${caseData.client.last_name || ""}`.trim())
                      : caseData?.client_name || "—"}
                  </p>
                </div>

                <div className="space-y-1">
                  <Label>Case Number</Label>
                  <p className="text-sm text-gray-500">{caseData?.case_number || caseData?.reference_number || "—"}</p>
                </div>

                <div className="col-span-2 space-y-1">
                  <Label>Description</Label>
                  {isEditing
                    ? <Textarea value={form.description} onChange={e => set("description", e.target.value)} rows={4} />
                    : <p className="text-sm text-gray-600">{caseData?.description || "No description provided."}</p>}
                </div>
              </div>
            </TabsContent>

            {/* ── NOTES TAB ── */}
            <TabsContent value="notes" className="space-y-4">
              <div className="flex gap-2">
                <Textarea
                  placeholder="Add a note..."
                  value={noteInput}
                  onChange={e => setNoteInput(e.target.value)}
                  rows={2}
                  className="flex-1"
                />
                <Button onClick={handleAddNote} disabled={addingNote || !noteInput.trim()} className="self-end">
                  {addingNote ? "Adding..." : "Add Note"}
                </Button>
              </div>
              {notesLoading ? (
                <div className="flex justify-center py-8">
                  <svg className="animate-spin h-6 w-6 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                  </svg>
                </div>
              ) : notes.length === 0 ? (
                <p className="text-sm text-gray-400 text-center py-8">No notes yet. Add one above.</p>
              ) : (
                <div className="space-y-3">
                  {notes.map((note, i) => (
                    <div key={note.id ?? i} className="border rounded-lg p-3 bg-gray-50 space-y-1">
                      <p className="text-sm">{note.content}</p>
                      <p className="text-xs text-gray-400">
                        {note.created_at
                          ? new Date(note.created_at).toLocaleString("en-ZA", { dateStyle: "medium", timeStyle: "short" })
                          : ""}
                        {note.is_pinned && <span className="ml-2 text-blue-500 font-medium">📌 Pinned</span>}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* ── DOCUMENTS TAB ── */}
            <TabsContent value="documents" className="space-y-4">
              <div className="flex justify-end">
                <Button size="sm" onClick={() => setShowUploadModal(true)}>+ Upload Document</Button>
              </div>
              <DocumentsList caseId={caseId} />
              <UploadDocumentModal open={showUploadModal} onOpenChange={setShowUploadModal} caseId={caseId} />
            </TabsContent>

            {/* ── FORMS TAB ── */}
            <TabsContent value="forms" className="space-y-4">

              {/* Header row */}
              <div className="flex justify-between items-center">
                <p className="text-sm text-slate-500">
                  Forms assigned to this case.
                </p>
                <Button size="sm" onClick={() => setShowAssignForm(true)}>
                  <Plus className="mr-1.5 h-3.5 w-3.5" />
                  Assign Form
                </Button>
              </div>

              {/* Assign form inline panel */}
              {showAssignForm && (
                <div className="border border-slate-200 rounded-lg p-4 bg-slate-50 space-y-3">
                  <p className="text-sm font-medium">Assign a Form Template</p>

                  {assignError && (
                    <p className="text-xs text-red-600 bg-red-50 border border-red-200 px-3 py-2 rounded">
                      {assignError}
                    </p>
                  )}

                  <div>
                    <Label className="text-xs mb-1 block">Template <span className="text-red-500">*</span></Label>
                    <select
                      value={assignTemplateId}
                      onChange={e => setAssignTemplateId(e.target.value)}
                      className="w-full border border-slate-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select a template...</option>
                      {templates
                        .filter(t => !assignments.find(a => a.template?.id === t.id))
                        .map(t => (
                          <option key={t.id} value={t.id}>
                            {t.name}
                            {t.case_type?.name ? ` [${t.case_type.name}]` : ""}
                          </option>
                        ))}
                    </select>
                  </div>

                  <div>
                    <Label className="text-xs mb-1 block">Due Date (optional)</Label>
                    <Input
                      type="date"
                      value={assignDueDate}
                      onChange={e => setAssignDueDate(e.target.value)}
                      className="text-sm"
                    />
                  </div>

                  <div className="flex justify-end gap-2">
                    <Button variant="outline" size="sm"
                      onClick={() => {
                        setShowAssignForm(false);
                        setAssignTemplateId("");
                        setAssignDueDate("");
                        setAssignError(null);
                      }}>
                      Cancel
                    </Button>
                    <Button size="sm" onClick={handleAssignForm} disabled={!assignTemplateId || assigning}>
                      {assigning ? "Assigning..." : "Assign"}
                    </Button>
                  </div>
                </div>
              )}

              {/* Assignments table */}
              {assignmentsLoading ? (
                <div className="py-8 text-center text-slate-400 text-sm">Loading forms...</div>
              ) : assignments.length === 0 ? (
                <div className="py-12 text-center text-slate-400 text-sm">
                  No forms assigned yet.
                </div>
              ) : (
                <div className="border border-slate-200 rounded-lg overflow-hidden">
                  <table className="w-full text-sm">
                    <thead className="bg-slate-50 border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
                      <tr>
                        <th className="px-4 py-3 text-left">Form</th>
                        <th className="px-4 py-3 text-left">Status</th>
                        <th className="px-4 py-3 text-left">Due Date</th>
                        <th className="px-4 py-3 text-left">Assigned By</th>
                        <th className="px-4 py-3 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200">
                      {assignments.map(a => (
                        <tr key={a.id} className="hover:bg-slate-50">
                          <td className="px-4 py-3 font-medium">
                            {a.template?.name ?? "—"}
                          </td>
                          <td className="px-4 py-3">
                            <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${FORM_STATUS_STYLES[a.status] ?? "bg-gray-100 text-gray-600"}`}>
                              {a.status === "approved"  && <CheckCircle className="h-3 w-3" />}
                              {a.status === "rejected"  && <XCircle className="h-3 w-3" />}
                              {a.is_overdue             && <Clock className="h-3 w-3 text-red-500" />}
                              {a.status_display ?? a.status}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-slate-500">
                            {a.due_date
                              ? <span className={a.is_overdue ? "text-red-600 font-medium" : ""}>
                                  {formatDeadlineDisplay(a.due_date)}
                                  {a.is_overdue && " ⚠️"}
                                </span>
                              : "—"}
                          </td>
                          <td className="px-4 py-3 text-slate-500">
                            {a.assigned_by?.name ?? "—"}
                          </td>
                          <td className="px-4 py-3 text-right">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleOpenReview(a)}
                            >
                              {["submitted", "approved", "rejected", "under_review"].includes(a.status)
                                ? "Review"
                                : "View"}
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </TabsContent>

            {/* ── MESSAGES TAB ── */}
<TabsContent value="messages" className="space-y-4">
  <div className="flex gap-2">
    <Textarea
      placeholder="Type a message to the client..."
      value={messageInput}
      onChange={e => setMessageInput(e.target.value)}
      rows={2}
      className="flex-1"
    />
    <Button
      onClick={handleSendMessage}
      disabled={sendingMessage || !messageInput.trim()}
      className="self-end"
    >
      {sendingMessage ? "Sending..." : "Send"}
    </Button>
  </div>

  {messagesLoading ? (
    <div className="flex justify-center py-8">
      <svg className="animate-spin h-6 w-6 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>
  ) : messages.length === 0 ? (
    <p className="text-sm text-gray-400 text-center py-8">
      No messages yet. Send the first one above.
    </p>
  ) : (
    <div className="space-y-3 max-h-80 overflow-y-auto">
      {messages.map((msg, i) => {
        const isLawyer = msg.sender_role !== "client"
        return (
          <div key={msg.id ?? i} className={`flex ${isLawyer ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm ${
              isLawyer
                ? "bg-blue-600 text-white rounded-br-md"
                : "bg-gray-100 text-gray-800 rounded-bl-md"
            }`}>
              <p>{msg.content}</p>
              <p className={`text-[11px] mt-1 ${isLawyer ? "text-blue-200" : "text-gray-400"}`}>
                {msg.created_at
                  ? new Date(msg.created_at).toLocaleString("en-ZA", {
                      dateStyle: "short", timeStyle: "short"
                    })
                  : ""}
              </p>
            </div>
          </div>
        )
      })}
    </div>
  )}
</TabsContent>

{/* ── TIME TAB ── */}
<TabsContent value="time" className="space-y-4">

  <div className="flex justify-between items-center">
    <div>
      <p className="text-sm text-slate-500">
        {timeLogs.length > 0 && (
          <span className="font-medium text-slate-700">
            {timeLogs.reduce((sum, l) => sum + parseFloat(l.duration), 0).toFixed(1)}h total
            {" · "}
            {timeLogs.filter(l => l.is_billable).reduce((sum, l) => sum + parseFloat(l.duration), 0).toFixed(1)}h billable
          </span>
        )}
      </p>
    </div>
    <Button size="sm" onClick={() => setShowTimeForm(true)}>
      <Plus className="mr-1.5 h-3.5 w-3.5" />
      Log Time
    </Button>
  </div>

  {/* Log time form */}
  {showTimeForm && (
    <div className="border border-slate-200 rounded-lg p-4 bg-slate-50 space-y-3">
      <p className="text-sm font-medium">New Time Entry</p>

      {timeError && (
        <p className="text-xs text-red-600 bg-red-50 border border-red-200 px-3 py-2 rounded">
          {timeError}
        </p>
      )}

      <div className="grid grid-cols-2 gap-3">
        <div>
          <Label className="text-xs mb-1 block">Date <span className="text-red-500">*</span></Label>
          <Input
            type="date"
            value={timeForm.date}
            onChange={e => setTimeForm(p => ({ ...p, date: e.target.value }))}
            className="text-sm"
          />
        </div>
        <div>
          <Label className="text-xs mb-1 block">Duration (hours) <span className="text-red-500">*</span></Label>
          <Input
            type="number"
            step="0.25"
            min="0.25"
            max="24"
            placeholder="e.g. 1.5"
            value={timeForm.duration}
            onChange={e => setTimeForm(p => ({ ...p, duration: e.target.value }))}
            className="text-sm"
          />
        </div>
      </div>

      <div>
        <Label className="text-xs mb-1 block">Activity Type</Label>
        <select
          value={timeForm.activity_type}
          onChange={e => setTimeForm(p => ({ ...p, activity_type: e.target.value }))}
          className="w-full border border-slate-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="research">Research</option>
          <option value="drafting">Drafting</option>
          <option value="call">Phone Call</option>
          <option value="meeting">Meeting</option>
          <option value="court">Court Appearance</option>
          <option value="review">Document Review</option>
          <option value="correspondence">Correspondence</option>
          <option value="filing">Filing</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div>
        <Label className="text-xs mb-1 block">Description <span className="text-red-500">*</span></Label>
        <Textarea
          placeholder="What did you work on?"
          value={timeForm.description}
          onChange={e => setTimeForm(p => ({ ...p, description: e.target.value }))}
          rows={2}
          className="text-sm"
        />
      </div>

      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="is_billable"
          checked={timeForm.is_billable}
          onChange={e => setTimeForm(p => ({ ...p, is_billable: e.target.checked }))}
          className="rounded"
        />
        <Label htmlFor="is_billable" className="text-sm cursor-pointer">
          Billable
        </Label>
      </div>

      <div className="flex justify-end gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            setShowTimeForm(false)
            setTimeError(null)
          }}
        >
          Cancel
        </Button>
        <Button
          size="sm"
          onClick={handleAddTimeLog}
          disabled={savingTime}
        >
          {savingTime ? "Saving..." : "Save Entry"}
        </Button>
      </div>
    </div>
  )}

  {/* Time logs list */}
  {timeLogsLoading ? (
    <div className="flex justify-center py-8">
      <svg className="animate-spin h-6 w-6 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>
  ) : timeLogs.length === 0 ? (
    <p className="text-sm text-gray-400 text-center py-8">
      No time logged yet.
    </p>
  ) : (
    <div className="border border-slate-200 rounded-lg overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-slate-50 border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-4 py-3 text-left">Date</th>
            <th className="px-4 py-3 text-left">Activity</th>
            <th className="px-4 py-3 text-left">Description</th>
            <th className="px-4 py-3 text-left">Hours</th>
            <th className="px-4 py-3 text-left">Billable</th>
            <th className="px-4 py-3 text-left">Logged By</th>
            <th className="px-4 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200">
          {timeLogs.map(log => (
            <tr key={log.id} className="hover:bg-slate-50">
              <td className="px-4 py-3 text-slate-600">
                {new Date(log.date).toLocaleDateString("en-ZA", {
                  day: "numeric", month: "short", year: "numeric"
                })}
              </td>
              <td className="px-4 py-3">
                <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded text-xs">
                  {log.activity_display}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-600 max-w-xs truncate">
                {log.description}
              </td>
              <td className="px-4 py-3 font-medium">
                {parseFloat(log.duration).toFixed(1)}h
              </td>
              <td className="px-4 py-3">
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                  log.is_billable
                    ? "bg-green-100 text-green-700"
                    : "bg-gray-100 text-gray-500"
                }`}>
                  {log.is_billable ? "Billable" : "Non-billable"}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-500">
                {log.logged_by?.name}
              </td>
              <td className="px-4 py-3 text-right">
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-red-500 hover:text-red-700 hover:bg-red-50"
                  onClick={() => handleDeleteTimeLog(log.id)}
                >
                  Delete
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )}
</TabsContent>
          </Tabs>
        )}
      </DialogContent>

        {/* EVERYTHING YOU CURRENTLY HAVE INSIDE DialogContent */}
    </Dialog>

    {/* REVIEW DRAWER */}
    {reviewingAssignment &&
      createPortal(
        <div className="fixed inset-0 z-[9999] flex justify-end">
          {/* backdrop */}
          <div
            className="absolute inset-0 bg-black/30"
            onClick={() => setReviewingAssignment(null)}
          />

          {/* drawer */}
          <div className="relative w-full max-w-xl bg-white shadow-xl flex flex-col max-h-full">

            {/* drawer header */}
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
              <div>
                <p className="font-semibold">
                  {reviewingAssignment.template?.name}
                </p>
                <p className="text-xs text-slate-500 mt-0.5">
                  {caseData?.reference_number} ·{" "}
                  <span
                    className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                      FORM_STATUS_STYLES[reviewingAssignment.status] ?? ""
                    }`}
                  >
                    {reviewingAssignment.status_display ??
                      reviewingAssignment.status}
                  </span>
                </p>
              </div>

              <button
                onClick={() => setReviewingAssignment(null)}
                className="text-slate-400 hover:text-slate-700 text-xl leading-none"
              >
                ×
              </button>
            </div>

            {/* drawer body */}
            <div className="flex-1 overflow-y-auto px-6 py-4">
              {/* ALL YOUR EXISTING DRAWER CONTENT GOES HERE */}
            </div>

            {/* drawer footer */}
            {submission?.is_complete && (
              <div className="px-6 py-4 border-t border-slate-200 space-y-3">
                {reviewError && (
                  <p className="text-xs text-red-600">{reviewError}</p>
                )}

                <div>
                  <Label className="text-xs mb-1 block">
                    Review Notes
                  </Label>

                  <Textarea
                    value={reviewNotes}
                    onChange={(e) => setReviewNotes(e.target.value)}
                    rows={2}
                    placeholder="Optional notes for the client..."
                    className="text-sm"
                  />
                </div>

                <div className="flex gap-2 justify-end">
                  <Button
                    size="sm"
                    variant="outline"
                    className="border-red-300 text-red-600 hover:bg-red-50"
                    onClick={() => handleReview("rejected")}
                    disabled={submitting}
                  >
                    <XCircle className="mr-1.5 h-3.5 w-3.5" />
                    {submitting ? "Saving..." : "Reject"}
                  </Button>

                  <Button
                    size="sm"
                    className="bg-green-600 hover:bg-green-700 text-white"
                    onClick={() => handleReview("approved")}
                    disabled={submitting}
                  >
                    <CheckCircle className="mr-1.5 h-3.5 w-3.5" />
                    {submitting ? "Saving..." : "Approve"}
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>,
        document.body
      )}
  </>
);


  // return (
  //   <Dialog open={open} onOpenChange={onOpenChange}>
 
  //     {/* ── REVIEW DRAWER ─────────────────────────────────────────────────── */}
  //     {reviewingAssignment && createPortal(
  //       <div className="fixed inset-0 z-[60] flex justify-end">
  //         {/* backdrop */}
  //         <div
  //           className="absolute inset-0 bg-black/30"
  //           onClick={() => setReviewingAssignment(null)}
  //         />

  //         {/* drawer */}
  //         <div className="relative w-full max-w-xl bg-white shadow-xl flex flex-col max-h-full">

  //           {/* drawer header */}
  //           <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
  //             <div>
  //               <p className="font-semibold">{reviewingAssignment.template?.name}</p>
  //               <p className="text-xs text-slate-500 mt-0.5">
  //                 {caseData?.reference_number} ·{" "}
  //                 <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${FORM_STATUS_STYLES[reviewingAssignment.status] ?? ""}`}>
  //                   {reviewingAssignment.status_display ?? reviewingAssignment.status}
  //                 </span>
  //               </p>
  //             </div>
  //             <button
  //               onClick={() => setReviewingAssignment(null)}
  //               className="text-slate-400 hover:text-slate-700 text-xl leading-none"
  //             >
  //               ×
  //             </button>
  //           </div>

  //           {/* drawer body */}
  //           <div className="flex-1 overflow-y-auto px-6 py-4">
  //             {reviewLoading ? (
  //               <div className="py-20 text-center text-slate-400 text-sm">
  //                 Loading submission...
  //               </div>
  //             ) : reviewError ? (
  //               <div className="rounded bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-600">
  //                 {reviewError}
  //               </div>
  //             ) : !submission ? (
  //               <div className="py-20 text-center text-slate-400 text-sm">
  //                 Client has not started this form yet.
  //               </div>
  //             ) : (
  //               <>
  //                 {/* submission meta */}
  //                 <div className="mb-4 text-xs text-slate-500 space-y-0.5">
  //                   <p>Submitted by: <span className="font-medium text-slate-700">{submission.submitted_by?.name ?? submission.submitted_by?.email}</span></p>
  //                   {submission.submitted_at && (
  //                     <p>Submitted at: <span className="font-medium text-slate-700">
  //                       {new Date(submission.submitted_at).toLocaleString("en-ZA", { dateStyle: "medium", timeStyle: "short" })}
  //                     </span></p>
  //                   )}
  //                   <p>Responses: <span className="font-medium text-slate-700">{submission.response_count ?? responses.length}</span></p>
  //                 </div>

  //                 {/* responses per section — accordion */}
  //                 {responses.length === 0 ? (
  //                   <p className="text-sm text-slate-400">No responses recorded.</p>
  //                 ) : (
  //                   <Accordion type="multiple" defaultValue={responsesBySection().map((_, i) => String(i))}>
  //                     {responsesBySection().map((section, i) => (
  //                       <AccordionItem key={i} value={String(i)}>
  //                         <AccordionTrigger>
  //                           <span className="font-medium">{section.label}</span>
  //                           <span className="ml-2 text-xs text-slate-400">
  //                             {section.responses.length} answers
  //                           </span>
  //                         </AccordionTrigger>
  //                         <AccordionContent>
  //                           <div className="space-y-4 pt-2">
  //                             {section.responses.map(r => (
  //                               <div key={r.id}>
  //                                 <p className="text-xs font-medium text-slate-600 mb-1">
  //                                   {r.question?.text}
  //                                   {r.question?.input_type && (
  //                                     <span className="ml-2 text-slate-400 font-normal">
  //                                       [{r.question.input_type}]
  //                                     </span>
  //                                   )}
  //                                 </p>
  //                                 <div className="bg-slate-50 border border-slate-200 rounded px-3 py-2 text-sm text-slate-800">
  //                                   {renderAnswer(r)}
  //                                 </div>
  //                               </div>
  //                             ))}
  //                           </div>
  //                         </AccordionContent>
  //                       </AccordionItem>
  //                     ))}
  //                   </Accordion>
  //                 )}

  //                 {/* previous review notes if any */}
  //                 {reviewingAssignment.review_notes && (
  //                   <div className="mt-4 rounded bg-yellow-50 border border-yellow-200 px-4 py-3">
  //                     <p className="text-xs font-medium text-yellow-800 mb-1">Previous Review Notes</p>
  //                     <p className="text-sm text-yellow-900">{reviewingAssignment.review_notes}</p>
  //                     {reviewingAssignment.reviewed_by && (
  //                       <p className="text-xs text-yellow-700 mt-1">
  //                         — {reviewingAssignment.reviewed_by.name},{" "}
  //                         {reviewingAssignment.reviewed_at
  //                           ? new Date(reviewingAssignment.reviewed_at).toLocaleDateString("en-ZA")
  //                           : ""}
  //                       </p>
  //                     )}
  //                   </div>
  //                 )}
  //               </>
  //             )}
  //           </div>

  //           {/* drawer footer — review actions */}
  //           {submission?.is_complete && (
  //             <div className="px-6 py-4 border-t border-slate-200 space-y-3">
  //               {reviewError && (
  //                 <p className="text-xs text-red-600">{reviewError}</p>
  //               )}
  //               <div>
  //                 <Label className="text-xs mb-1 block">Review Notes</Label>
  //                 <Textarea
  //                   value={reviewNotes}
  //                   onChange={e => setReviewNotes(e.target.value)}
  //                   rows={2}
  //                   placeholder="Optional notes for the client..."
  //                   className="text-sm"
  //                 />
  //               </div>
  //               <div className="flex gap-2 justify-end">
  //                 <Button
  //                   size="sm"
  //                   variant="outline"
  //                   className="border-red-300 text-red-600 hover:bg-red-50"
  //                   onClick={() => handleReview("rejected")}
  //                   disabled={submitting}
  //                 >
  //                   <XCircle className="mr-1.5 h-3.5 w-3.5" />
  //                   {submitting ? "Saving..." : "Reject"}
  //                 </Button>
  //                 <Button
  //                   size="sm"
  //                   className="bg-green-600 hover:bg-green-700 text-white"
  //                   onClick={() => handleReview("approved")}
  //                   disabled={submitting}
  //                 >
  //                   <CheckCircle className="mr-1.5 h-3.5 w-3.5" />
  //                   {submitting ? "Saving..." : "Approve"}
  //                 </Button>
  //               </div>
  //             </div>
  //           )}
  //         </div>
  //       </div>
  //     )}
  //   </Dialog>
  // );
}

export default ViewCaseModal;
