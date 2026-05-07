"use client";

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
import { DocumentsList } from "./DocumentsList"

import { UploadDocumentModal } from "./UploadDocumentModal"
import {
  getCaseDetails, getCaseNotes, addNote, updateCase,
  assignToCase, getFirmMembers, getAllMatterTypes,
} from "@/lib/api/cases";

// ✅ Safe deadline parser — handles ISO strings, date-only, null/undefined
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

// ✅ FIX 3: Normalise status from API (e.g. "new" → display "New", keep value as-is for updates)
const STATUS_OPTIONS = [
  { value: "new",     label: "New" },
  { value: "active",  label: "Active" },
  { value: "pending", label: "Pending" },
  { value: "closed",  label: "Closed" },
];

export function ViewCaseModal({ open, onOpenChange, caseId, onUpdate }) {
  const [caseData, setCaseData]           = useState(null);
  const [loading, setLoading]             = useState(false);
  const [isEditing, setIsEditing]         = useState(false);
  const [savingCase, setSavingCase]       = useState(false);
  const [saveError, setSaveError]         = useState(null);

  const [notes, setNotes]                 = useState([]);
  const [noteInput, setNoteInput]         = useState("");
  const [notesLoading, setNotesLoading]   = useState(false);
  const [addingNote, setAddingNote]       = useState(false);

  const [form, setForm] = useState({
    title: "", description: "", status: "", priority: "",
    matter_type: "", deadline: "",
  });

  const [members, setMembers]             = useState([]);
  const [matterTypes, setMatterTypes]     = useState([]);
  const [selectedUser, setSelectedUser]   = useState("");
  const [showUploadModal, setShowUploadModal] = useState(false);

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
      // ✅ FIX 1: API returns res directly (already unwrapped in cases.js as res.data.data)
      // So res is the array. Handle both shapes.
      setMembers(Array.isArray(res) ? res : res.data || []);
    } catch (err) { console.error("Failed to load members", err); }
  };

  const fetchMatterTypes = async () => {
    try {
      const res = await getAllMatterTypes();
      setMatterTypes(Array.isArray(res) ? res : res.data || []);
    } catch (err) { console.error("Failed to load matter types", err); }
  };

  const fetchCase = async () => {
    setLoading(true);
    try {
      const res = await getCaseDetails(caseId);
      const data = res.data || res;
      setCaseData(data);
    } catch (err) { console.error("Failed to load case", err); }
    finally { setLoading(false); }
  };

  useEffect(() => {
    if (open) {
      fetchMembers();
      fetchMatterTypes();
      if (caseId) { fetchCase(); fetchNotes(); }
    }
    if (!open) { setIsEditing(false); setSaveError(null); }
  }, [open, caseId]);

  // ✅ FIX 2: Populate form safely with parseDeadline
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
    }
  }, [caseData]);

  const set = (key, value) => setForm(prev => ({ ...prev, [key]: value }));

  const handleSave = async () => {
    setSavingCase(true);
    setSaveError(null);
    try {
      const payload = {
        title:       form.title,
        description: form.description,
        status:      form.status,
        priority:    form.priority,
        deadline:    form.deadline || null,
      };
      if (form.matter_type) payload.matter_type = Number(form.matter_type);
      await updateCase(caseId, payload);
      if (selectedUser) {
        await assignToCase(caseId, { user_id: Number(selectedUser) });
      }
      setIsEditing(false);
      await fetchCase();
      onUpdate?.(); // ✅ Refresh parent cases list
    } catch (err) {
      console.error("Update failed", err);
      setSaveError("Failed to save changes. Please try again.");
    } finally { setSavingCase(false); }
  };

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

  if (!caseId) return null;

  return (
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
            </TabsList>

            {/* ── DETAILS TAB ── */}
            <TabsContent value="details" className="space-y-4">
              {saveError && (
                <p className="text-sm text-red-500 bg-red-50 px-3 py-2 rounded">{saveError}</p>
              )}
              <div className="grid grid-cols-2 gap-4">

                {/* Case Title */}
                <div className="col-span-2 space-y-1">
                  <Label>Case Title</Label>
                  {isEditing
                    ? <Input value={form.title} onChange={e => set("title", e.target.value)} />
                    : <p className="text-sm font-medium">{caseData?.title || "—"}</p>}
                </div>

                {/* Status — ✅ FIX 3: includes "new" + "pending" options */}
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

                {/* Deadline — ✅ FIX 2: parseDeadline used */}
                <div className="space-y-1">
                  <Label>Deadline</Label>
                  {isEditing
                    ? <Input type="date" value={form.deadline} onChange={e => set("deadline", e.target.value)} />
                    : <p className="text-sm">{formatDeadlineDisplay(caseData?.deadline)}</p>}
                </div>

                {/* Matter Type */}
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

                {/* Assigned Lawyer — ✅ FIX 1: use m.name not m.first_name + m.last_name */}
                <div className="space-y-1">
                  <Label>Assigned Lawyer</Label>
                  {isEditing ? (
                    <Select value={selectedUser} onValueChange={setSelectedUser}>
                      <SelectTrigger><SelectValue placeholder="Assign a lawyer" /></SelectTrigger>
                      <SelectContent>
                        {members
                          .filter(m => m.role === "lawyer")
                          .map(m => (
                            <SelectItem key={String(m.id)} value={String(m.id)}>
                              {m.name}
                            </SelectItem>
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

                {/* Client */}
                <div className="space-y-1">
                  <Label>Client</Label>
                  <p className="text-sm">
                    {caseData?.client
                      ? (caseData.client.name || `${caseData.client.first_name || ""} ${caseData.client.last_name || ""}`.trim())
                      : caseData?.client_name || "—"}
                  </p>
                </div>

                {/* Case Number */}
                <div className="space-y-1">
                  <Label>Case Number</Label>
                  <p className="text-sm text-gray-500">{caseData?.case_number || "—"}</p>
                </div>

                {/* Description */}
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
          </Tabs>
        )}
      </DialogContent>
    </Dialog>
  );
}

export default ViewCaseModal;

// "use client";

// import { useState, useEffect } from "react";
// import {
//   Dialog, DialogContent, DialogHeader, DialogTitle,
// } from "@/components/ui/dialog";
// import { Button } from "@/components/ui/button";
// import { Label } from "@/components/ui/label";
// import { Input } from "@/components/ui/input";
// import { Textarea } from "@/components/ui/textarea";
// import {
//   Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
// } from "@/components/ui/select";
// import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
// // import DocumentsList from "@/components/cases/DocumentsList";
// import { DocumentsList } from "./DocumentsList"

// // import DocumentsList from "@/components/cases/DocumentsList";
// import { UploadDocumentModal } from "./UploadDocumentModal"
// import {
//   getCaseDetails, getCaseNotes, addNote, updateCase,
//   assignToCase, getFirmMembers, getAllMatterTypes,
// } from "@/lib/api/cases";

// // ✅ Safe deadline parser — handles ISO strings, date-only, null/undefined
// function parseDeadline(deadline) {
//   if (!deadline) return "";
//   if (typeof deadline === "string" && deadline.includes("T")) return deadline.split("T")[0];
//   if (typeof deadline === "string" && /^\d{4}-\d{2}-\d{2}$/.test(deadline)) return deadline;
//   try { return new Date(deadline).toISOString().split("T")[0]; } catch { return ""; }
// }

// function formatDeadlineDisplay(deadline) {
//   const parsed = parseDeadline(deadline);
//   if (!parsed) return "—";
//   try {
//     return new Date(parsed + "T00:00:00").toLocaleDateString("en-ZA", {
//       year: "numeric", month: "long", day: "numeric",
//     });
//   } catch { return parsed; }
// }

// // // ✅ FIX 3: Normalise status from API (e.g. "new" → display "New", keep value as-is for updates)
// // const STATUS_OPTIONS = [
// //   { value: "new",     label: "New" },
// //   { value: "active",  label: "Active" },
// //   { value: "pending", label: "Pending" },
// //   { value: "closed",  label: "Closed" },
// // ];

// export function ViewCaseModal({ open, onOpenChange, caseId, onUpdate }) {
//   const [caseData, setCaseData]           = useState(null);
//   const [loading, setLoading]             = useState(false);
//   const [isEditing, setIsEditing]         = useState(false);
//   const [savingCase, setSavingCase]       = useState(false);
//   const [saveError, setSaveError]         = useState(null);

//   const [notes, setNotes]                 = useState([]);
//   const [noteInput, setNoteInput]         = useState("");
//   const [notesLoading, setNotesLoading]   = useState(false);
//   const [addingNote, setAddingNote]       = useState(false);

//   const [form, setForm] = useState({
//     title: "", description: "", status: "", priority: "",
//     matter_type: "", deadline: "",
//   });

//   const [members, setMembers]             = useState([]);
//   const [matterTypes, setMatterTypes]     = useState([]);
//   const [selectedUser, setSelectedUser]   = useState("");
//   const [showUploadModal, setShowUploadModal] = useState(false);

//   const fetchNotes = async () => {
//     setNotesLoading(true);
//     try {
//       const res = await getCaseNotes(caseId);
//       const data = res.data || res;
//       setNotes(Array.isArray(data) ? data : []);
//     } catch (err) { console.error("Failed to load notes", err); }
//     finally { setNotesLoading(false); }
//   };

//   const fetchMembers = async () => {
//     try {
//       const res = await getFirmMembers();
//       // ✅ FIX 1: API returns res directly (already unwrapped in cases.js as res.data.data)
//       // So res is the array. Handle both shapes.
//       setMembers(Array.isArray(res) ? res : res.data || []);
//     } catch (err) { console.error("Failed to load members", err); }
//   };

//   const fetchMatterTypes = async () => {
//     try {
//       const res = await getAllMatterTypes();
//       setMatterTypes(Array.isArray(res) ? res : res.data || []);
//     } catch (err) { console.error("Failed to load matter types", err); }
//   };

//   const fetchCase = async () => {
//     setLoading(true);
//     try {
//       const res = await getCaseDetails(caseId);
//       const data = res.data || res;
//       setCaseData(data);
//     } catch (err) { console.error("Failed to load case", err); }
//     finally { setLoading(false); }
//   };

//   useEffect(() => {
//     if (open) {
//       fetchMembers();
//       fetchMatterTypes();
//       if (caseId) { fetchCase(); fetchNotes(); }
//     }
//     if (!open) { setIsEditing(false); setSaveError(null); }
//   }, [open, caseId]);

//   // ✅ FIX 2: Populate form safely with parseDeadline
//   useEffect(() => {
//     if (caseData) {
//       setForm({
//         title:       caseData.title || "",
//         description: caseData.description || "",
//         status:      caseData.status || "",
//         priority:    caseData.priority || "",
//         matter_type: caseData.matter_type?.id?.toString() || "",
//         deadline:    parseDeadline(caseData.deadline),
//       });
//     }
//   }, [caseData]);

//   useEffect(() => {
//     if (caseData?.assigned_lawyer) {
//       setSelectedUser(caseData.assigned_lawyer.id?.toString() || "");
//     }
//   }, [caseData]);

//   const set = (key, value) => setForm(prev => ({ ...prev, [key]: value }));

//   const handleSave = async () => {
//     setSavingCase(true);
//     setSaveError(null);
//     try {
//       const payload = {
//         title:       form.title,
//         description: form.description,
//         status:      form.status,
//         priority:    form.priority,
//         deadline:    form.deadline || null,
//       };
//       if (form.matter_type) payload.matter_type = Number(form.matter_type);
//       await updateCase(caseId, payload);
//       if (selectedUser) {
//         await assignToCase(caseId, { user_id: Number(selectedUser) });
//       }
//       setIsEditing(false);
//       await fetchCase();
//       onUpdate?.(); // ✅ Refresh parent cases list
//     } catch (err) {
//       console.error("Update failed", err);
//       setSaveError("Failed to save changes. Please try again.");
//     } finally { setSavingCase(false); }
//   };

//   const handleAddNote = async () => {
//     if (!noteInput.trim()) return;
//     setAddingNote(true);
//     try {
//       await addNote(caseId, { content: noteInput, is_pinned: false });
//       setNoteInput("");
//       await fetchNotes();
//     } catch (err) { console.error("Failed to add note", err); }
//     finally { setAddingNote(false); }
//   };

//   if (!caseId) return null;

//   return (
//     <Dialog open={open} onOpenChange={onOpenChange}>
//       <DialogContent className="sm:max-w-[900px] max-h-[90vh] overflow-y-auto">
//         <DialogHeader className="flex flex-row justify-between items-center">
//           <DialogTitle className="text-lg font-semibold">
//             {loading ? "Loading..." : caseData?.title || "Case Details"}
//           </DialogTitle>
//           <div className="flex gap-2">
//             {isEditing ? (
//               <>
//                 <Button variant="outline" size="sm"
//                   onClick={() => { setIsEditing(false); setSaveError(null); }}>
//                   Cancel
//                 </Button>
//                 <Button size="sm" onClick={handleSave} disabled={savingCase}>
//                   {savingCase ? "Saving..." : "Save Changes"}
//                 </Button>
//               </>
//             ) : (
//               <Button size="sm" onClick={() => setIsEditing(true)}>Edit</Button>
//             )}
//           </div>
//         </DialogHeader>

//         {loading ? (
//           <div className="flex items-center justify-center py-16">
//             <div className="flex flex-col items-center gap-3 text-gray-400">
//               <svg className="animate-spin h-8 w-8" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
//                 <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
//                 <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
//               </svg>
//               <span className="text-sm">Loading case details...</span>
//             </div>
//           </div>
//         ) : (
//           <Tabs defaultValue="details">
//             <TabsList className="mb-4">
//               <TabsTrigger value="details">Details</TabsTrigger>
//               <TabsTrigger value="notes">Notes ({notes.length})</TabsTrigger>
//               <TabsTrigger value="documents">Documents</TabsTrigger>
//             </TabsList>

//             {/* ── DETAILS TAB ── */}
//             <TabsContent value="details" className="space-y-4">
//               {saveError && (
//                 <p className="text-sm text-red-500 bg-red-50 px-3 py-2 rounded">{saveError}</p>
//               )}
//               <div className="grid grid-cols-2 gap-4">

//                 {/* Case Title */}
//                 <div className="col-span-2 space-y-1">
//                   <Label>Case Title</Label>
//                   {isEditing
//                     ? <Input value={form.title} onChange={e => set("title", e.target.value)} />
//                     : <p className="text-sm font-medium">{caseData?.title || "—"}</p>}
//                 </div>

//                 {/* Status — ✅ FIX 3: includes "new" + "pending" options */}
//                 <div className="space-y-1">
//                   <Label>Status</Label>
//                   {isEditing ? (
//                     <Select value={form.status} onValueChange={v => set("status", v)}>
//                       <SelectTrigger><SelectValue placeholder="Select status" /></SelectTrigger>
//                       <SelectContent>
//                         {STATUS_OPTIONS.map(s => (
//                           <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
//                         ))}
//                       </SelectContent>
//                     </Select>
//                   ) : (
//                     <span className={`inline-block text-xs px-2 py-1 rounded-full font-medium capitalize ${
//                       caseData?.status === "active"  ? "bg-green-100 text-green-700"  :
//                       caseData?.status === "pending" ? "bg-yellow-100 text-yellow-700":
//                       caseData?.status === "closed"  ? "bg-gray-100 text-gray-500"    :
//                       "bg-blue-100 text-blue-600"
//                     }`}>
//                       {caseData?.status || "—"}
//                     </span>
//                   )}
//                 </div>

//                 {/* Deadline — ✅ FIX 2: parseDeadline used */}
//                 <div className="space-y-1">
//                   <Label>Deadline</Label>
//                   {isEditing
//                     ? <Input type="date" value={form.deadline} onChange={e => set("deadline", e.target.value)} />
//                     : <p className="text-sm">{formatDeadlineDisplay(caseData?.deadline)}</p>}
//                 </div>

//                 {/* Matter Type */}
//                 <div className="space-y-1">
//                   <Label>Matter Type</Label>
//                   {isEditing ? (
//                     <Select value={form.matter_type} onValueChange={v => set("matter_type", v)}>
//                       <SelectTrigger><SelectValue placeholder="Select matter type" /></SelectTrigger>
//                       <SelectContent>
//                         {matterTypes.map(mt => (
//                           <SelectItem key={String(mt.id ?? mt.name)} value={String(mt.id)}>
//                             {mt.name}
//                           </SelectItem>
//                         ))}
//                       </SelectContent>
//                     </Select>
//                   ) : (
//                     <p className="text-sm">{caseData?.matter_type?.name || "—"}</p>
//                   )}
//                 </div>

//                 {/* Assigned Lawyer — ✅ FIX 1: use m.name not m.first_name + m.last_name */}
//                 <div className="space-y-1">
//                   <Label>Assigned Lawyer</Label>
//                   {isEditing ? (
//                     <Select value={selectedUser} onValueChange={setSelectedUser}>
//                       <SelectTrigger><SelectValue placeholder="Assign a lawyer" /></SelectTrigger>
//                       <SelectContent>
//                         {members
//                           .filter(m => m.role === "lawyer")
//                           .map(m => (
//                             <SelectItem key={String(m.id)} value={String(m.id)}>
//                               {m.name}
//                             </SelectItem>
//                           ))}
//                       </SelectContent>
//                     </Select>
//                   ) : (
//                     <p className="text-sm">
//                       {caseData?.assigned_lawyer
//                         ? (caseData.assigned_lawyer.name ||
//                            `${caseData.assigned_lawyer.first_name || ""} ${caseData.assigned_lawyer.last_name || ""}`.trim() ||
//                            "Unassigned")
//                         : "Unassigned"}
//                     </p>
//                   )}
//                 </div>

//                 {/* Client */}
//                 <div className="space-y-1">
//                   <Label>Client</Label>
//                   <p className="text-sm">
//                     {caseData?.client
//                       ? (caseData.client.name || `${caseData.client.first_name || ""} ${caseData.client.last_name || ""}`.trim())
//                       : caseData?.client_name || "—"}
//                   </p>
//                 </div>

//                 {/* Case Number */}
//                 <div className="space-y-1">
//                   <Label>Case Number</Label>
//                   <p className="text-sm text-gray-500">{caseData?.case_number || "—"}</p>
//                 </div>

//                 {/* Description */}
//                 <div className="col-span-2 space-y-1">
//                   <Label>Description</Label>
//                   {isEditing
//                     ? <Textarea value={form.description} onChange={e => set("description", e.target.value)} rows={4} />
//                     : <p className="text-sm text-gray-600">{caseData?.description || "No description provided."}</p>}
//                 </div>
//               </div>
//             </TabsContent>

//             {/* ── NOTES TAB ── */}
//             <TabsContent value="notes" className="space-y-4">
//               <div className="flex gap-2">
//                 <Textarea
//                   placeholder="Add a note..."
//                   value={noteInput}
//                   onChange={e => setNoteInput(e.target.value)}
//                   rows={2}
//                   className="flex-1"
//                 />
//                 <Button onClick={handleAddNote} disabled={addingNote || !noteInput.trim()} className="self-end">
//                   {addingNote ? "Adding..." : "Add Note"}
//                 </Button>
//               </div>

//               {notesLoading ? (
//                 <div className="flex justify-center py-8">
//                   <svg className="animate-spin h-6 w-6 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
//                     <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
//                     <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
//                   </svg>
//                 </div>
//               ) : notes.length === 0 ? (
//                 <p className="text-sm text-gray-400 text-center py-8">No notes yet. Add one above.</p>
//               ) : (
//                 <div className="space-y-3">
//                   {notes.map((note, i) => (
//                     <div key={note.id ?? i} className="border rounded-lg p-3 bg-gray-50 space-y-1">
//                       <p className="text-sm">{note.content}</p>
//                       <p className="text-xs text-gray-400">
//                         {note.created_at
//                           ? new Date(note.created_at).toLocaleString("en-ZA", { dateStyle: "medium", timeStyle: "short" })
//                           : ""}
//                         {note.is_pinned && <span className="ml-2 text-blue-500 font-medium">📌 Pinned</span>}
//                       </p>
//                     </div>
//                   ))}
//                 </div>
//               )}
//             </TabsContent>

//             {/* ── DOCUMENTS TAB ── */}
//             <TabsContent value="documents" className="space-y-4">
//               <div className="flex justify-end">
//                 <Button size="sm" onClick={() => setShowUploadModal(true)}>+ Upload Document</Button>
//               </div>
//               <DocumentsList caseId={caseId} />
//               <UploadDocumentModal open={showUploadModal} onOpenChange={setShowUploadModal} caseId={caseId} />
//             </TabsContent>
//           </Tabs>
//         )}
//       </DialogContent>
//     </Dialog>
//   );
// }

// export default ViewCaseModal;

// "use client";

// import { useState, useEffect } from "react";
// import {
//   Dialog,
//   DialogContent,
//   DialogHeader,
//   DialogTitle,
// } from "@/components/ui/dialog";
// import { Button } from "@/components/ui/button";
// import { Label } from "@/components/ui/label";
// import { Input } from "@/components/ui/input";
// import { Textarea } from "@/components/ui/textarea";
// import {
//   Select,
//   SelectContent,
//   SelectItem,
//   SelectTrigger,
//   SelectValue,
// } from "@/components/ui/select";
// import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
// import { DocumentsList } from "./DocumentsList"

// // import DocumentsList from "@/components/cases/DocumentsList";
// import { UploadDocumentModal } from "./UploadDocumentModal"
// import {
//   getCaseDetails,
//   getCaseNotes,
//   addNote,
//   updateCase,
//   assignToCase,
//   getFirmMembers,
//   getAllMatterTypes,
// } from "@/lib/api/cases";

// // ✅ FIX 1: Safe deadline parser — handles ISO strings, date-only strings, and null/undefined
// function parseDeadline(deadline) {
//   if (!deadline) return "";
//   // If it's an ISO string like "2026-05-30T00:00:00Z" or "2026-05-30T00:00:00.000Z"
//   if (typeof deadline === "string" && deadline.includes("T")) {
//     return deadline.split("T")[0];
//   }
//   // If it's already "YYYY-MM-DD"
//   if (typeof deadline === "string" && /^\d{4}-\d{2}-\d{2}$/.test(deadline)) {
//     return deadline;
//   }
//   // If it's a Date object or timestamp
//   try {
//     return new Date(deadline).toISOString().split("T")[0];
//   } catch {
//     return "";
//   }
// }

// // ✅ FIX 2: Format deadline for display (e.g. "May 30, 2026")
// function formatDeadlineDisplay(deadline) {
//   const parsed = parseDeadline(deadline);
//   if (!parsed) return "—";
//   try {
//     return new Date(parsed + "T00:00:00").toLocaleDateString("en-ZA", {
//       year: "numeric",
//       month: "long",
//       day: "numeric",
//     });
//   } catch {
//     return parsed;
//   }
// }

// export function ViewCaseModal({ open, onOpenChange, caseId, onUpdate }) {
//   const [caseData, setCaseData] = useState(null);
//   const [loading, setLoading] = useState(false);
//   const [isEditing, setIsEditing] = useState(false);
//   const [notes, setNotes] = useState([]);
//   const [noteInput, setNoteInput] = useState("");
//   const [notesLoading, setNotesLoading] = useState(false);
//   const [addingNote, setAddingNote] = useState(false);
//   const [savingCase, setSavingCase] = useState(false);
//   const [saveError, setSaveError] = useState(null);

//   const [form, setForm] = useState({
//     title: "",
//     description: "",
//     status: "",
//     priority: "",
//     matter_type: "",
//     deadline: "",
//   });

//   const [members, setMembers] = useState([]);
//   const [matterTypes, setMatterTypes] = useState([]);
//   const [selectedUser, setSelectedUser] = useState("");
//   const [showUploadModal, setShowUploadModal] = useState(false);

//   const fetchNotes = async () => {
//     try {
//       setNotesLoading(true);
//       const res = await getCaseNotes(caseId);
//       const data = res.data || res;
//       setNotes(Array.isArray(data) ? data : []);
//     } catch (err) {
//       console.error("Failed to load notes", err);
//     } finally {
//       setNotesLoading(false);
//     }
//   };

//   const fetchMembers = async () => {
//     try {
//       const res = await getFirmMembers();
//       setMembers(Array.isArray(res) ? res : res.data || []);
//     } catch (err) {
//       console.error("Failed to load members", err);
//     }
//   };

//   const fetchMatterTypes = async () => {
//     try {
//       const res = await getAllMatterTypes();
//       setMatterTypes(res.data || []);
//     } catch (err) {
//       console.error("Failed to load matter types", err);
//     }
//   };

//   const fetchCase = async () => {
//     try {
//       setLoading(true);
//       const res = await getCaseDetails(caseId);
//       const data = res.data || res;
//       setCaseData(data);
//     } catch (err) {
//       console.error("Failed to load case", err);
//     } finally {
//       setLoading(false);
//     }
//   };

//   useEffect(() => {
//     if (open) {
//       fetchMembers();
//       fetchMatterTypes();
//       if (caseId) {
//         fetchCase();
//         fetchNotes();
//       }
//     }
//     // Reset editing state when modal closes
//     if (!open) {
//       setIsEditing(false);
//       setSaveError(null);
//     }
//   }, [open, caseId]);

//   // ✅ FIX 3: Populate form when caseData loads, using safe deadline parser
//   useEffect(() => {
//     if (caseData) {
//       setForm({
//         title: caseData.title || "",
//         description: caseData.description || "",
//         status: caseData.status || "",
//         priority: caseData.priority || "",
//         matter_type: caseData.matter_type?.id?.toString() || "",
//         // ✅ KEY FIX: Use parseDeadline instead of raw .split("T")[0]
//         deadline: parseDeadline(caseData.deadline),
//       });
//     }
//   }, [caseData]);

//   useEffect(() => {
//     if (caseData?.assigned_lawyer) {
//       setSelectedUser(caseData.assigned_lawyer.id?.toString() || "");
//     }
//   }, [caseData]);

//   const set = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

//   const handleSave = async () => {
//     setSavingCase(true);
//     setSaveError(null);
//     try {
//       const payload = {
//         title: form.title,
//         description: form.description,
//         status: form.status,
//         priority: form.priority,
//       };
//       if (form.matter_type) payload.matter_type = Number(form.matter_type);
//       // ✅ FIX 4: Always include deadline in payload (even if empty, send null)
//       payload.deadline = form.deadline || null;

//       await updateCase(caseId, payload);

//       if (selectedUser) {
//         await assignToCase(caseId, { user_id: Number(selectedUser) });
//       }

//       setIsEditing(false);
//       await fetchCase();
//       // ✅ FIX 5: Notify parent to refresh the cases list
//       onUpdate?.();
//     } catch (err) {
//       console.error("Update failed", err);
//       setSaveError("Failed to save changes. Please try again.");
//     } finally {
//       setSavingCase(false);
//     }
//   };

//   const handleAddNote = async () => {
//     if (!noteInput.trim()) return;
//     setAddingNote(true);
//     try {
//       await addNote(caseId, { content: noteInput, is_pinned: false });
//       setNoteInput("");
//       await fetchNotes();
//     } catch (err) {
//       console.error("Failed to add note", err);
//     } finally {
//       setAddingNote(false);
//     }
//   };

//   if (!caseId) return null;

//   return (
//     <Dialog open={open} onOpenChange={onOpenChange}>
//       <DialogContent className="sm:max-w-[900px] max-h-[90vh] overflow-y-auto">
//         <DialogHeader className="flex flex-row justify-between items-center">
//           <DialogTitle className="text-lg font-semibold">
//             {loading ? "Loading..." : caseData?.title || "Case Details"}
//           </DialogTitle>
//           <div className="flex gap-2">
//             {isEditing ? (
//               <>
//                 <Button variant="outline" size="sm" onClick={() => { setIsEditing(false); setSaveError(null); }}>
//                   Cancel
//                 </Button>
//                 <Button size="sm" onClick={handleSave} disabled={savingCase}>
//                   {savingCase ? "Saving..." : "Save Changes"}
//                 </Button>
//               </>
//             ) : (
//               <Button size="sm" onClick={() => setIsEditing(true)}>
//                 Edit
//               </Button>
//             )}
//           </div>
//         </DialogHeader>

//         {loading ? (
//           <div className="flex items-center justify-center py-16">
//             <div className="flex flex-col items-center gap-3 text-gray-400">
//               <svg className="animate-spin h-8 w-8" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
//                 <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
//                 <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
//               </svg>
//               <span className="text-sm">Loading case details...</span>
//             </div>
//           </div>
//         ) : (
//           <Tabs defaultValue="details">
//             <TabsList className="mb-4">
//               <TabsTrigger value="details">Details</TabsTrigger>
//               <TabsTrigger value="notes">Notes ({notes.length})</TabsTrigger>
//               <TabsTrigger value="documents">Documents</TabsTrigger>
//             </TabsList>

//             {/* ── DETAILS TAB ── */}
//             <TabsContent value="details" className="space-y-4">
//               {saveError && (
//                 <p className="text-sm text-red-500 bg-red-50 px-3 py-2 rounded">{saveError}</p>
//               )}

//               <div className="grid grid-cols-2 gap-4">
//                 {/* Title */}
//                 <div className="col-span-2 space-y-1">
//                   <Label>Case Title</Label>
//                   {isEditing ? (
//                     <Input value={form.title} onChange={(e) => set("title", e.target.value)} />
//                   ) : (
//                     <p className="text-sm font-medium">{caseData?.title || "—"}</p>
//                   )}
//                 </div>

//                 {/* Status */}
//                 <div className="space-y-1">
//                   <Label>Status</Label>
//                   {isEditing ? (
//                     <Select value={form.status} onValueChange={(v) => set("status", v)}>
//                       <SelectTrigger><SelectValue /></SelectTrigger>
//                       <SelectContent>
//                         <SelectItem value="active">Active</SelectItem>
//                         <SelectItem value="pending">Pending</SelectItem>
//                         <SelectItem value="closed">Closed</SelectItem>
//                       </SelectContent>
//                     </Select>
//                   ) : (
//                     <span className={`inline-block text-xs px-2 py-1 rounded-full font-medium ${
//                       caseData?.status === "active" ? "bg-green-100 text-green-700" :
//                       caseData?.status === "pending" ? "bg-yellow-100 text-yellow-700" :
//                       "bg-gray-100 text-gray-600"
//                     }`}>
//                       {caseData?.status ? caseData.status.charAt(0).toUpperCase() + caseData.status.slice(1) : "—"}
//                     </span>
//                   )}
//                 </div>

//                 {/* Deadline — ✅ FIX 6: Display uses formatDeadlineDisplay, edit uses parseDeadline */}
//                 <div className="space-y-1">
//                   <Label>Deadline</Label>
//                   {isEditing ? (
//                     <Input
//                       type="date"
//                       value={form.deadline}
//                       onChange={(e) => set("deadline", e.target.value)}
//                     />
//                   ) : (
//                     <p className="text-sm">{formatDeadlineDisplay(caseData?.deadline)}</p>
//                   )}
//                 </div>

//                 {/* Matter Type */}
//                 <div className="space-y-1">
//                   <Label>Matter Type</Label>
//                   {isEditing ? (
//                     <Select value={form.matter_type} onValueChange={(v) => set("matter_type", v)}>
//                       <SelectTrigger><SelectValue placeholder="Select matter type" /></SelectTrigger>
//                       <SelectContent>
//                         {matterTypes.map((mt) => (
//                           <SelectItem key={String(mt.id ?? mt.name)} value={String(mt.id)}>
//                             {mt.name}
//                           </SelectItem>
//                         ))}
//                       </SelectContent>
//                     </Select>
//                   ) : (
//                     <p className="text-sm">{caseData?.matter_type?.name || "—"}</p>
//                   )}
//                 </div>

//                 {/* Assigned Lawyer */}
//                 <div className="space-y-1">
//                   <Label>Assigned Lawyer</Label>
//                   {isEditing ? (
//                     <Select value={selectedUser} onValueChange={setSelectedUser}>
//                       <SelectTrigger><SelectValue placeholder="Assign a lawyer" /></SelectTrigger>
//                       <SelectContent>
//                         {members.map((m) => (
//                           <SelectItem key={String(m.id)} value={String(m.id)}>
//                             {m.first_name} {m.last_name}
//                           </SelectItem>
//                         ))}
//                       </SelectContent>
//                     </Select>
//                   ) : (
//                     <p className="text-sm">
//                       {caseData?.assigned_lawyer
//                         ? `${caseData.assigned_lawyer.first_name} ${caseData.assigned_lawyer.last_name}`
//                         : "Unassigned"}
//                     </p>
//                   )}
//                 </div>

//                 {/* Client */}
//                 <div className="space-y-1">
//                   <Label>Client</Label>
//                   <p className="text-sm">
//                     {caseData?.client
//                       ? `${caseData.client.first_name} ${caseData.client.last_name}`
//                       : caseData?.client_name || "—"}
//                   </p>
//                 </div>

//                 {/* Case Number */}
//                 <div className="space-y-1">
//                   <Label>Case Number</Label>
//                   <p className="text-sm text-gray-500">{caseData?.case_number || "—"}</p>
//                 </div>

//                 {/* Description */}
//                 <div className="col-span-2 space-y-1">
//                   <Label>Description</Label>
//                   {isEditing ? (
//                     <Textarea
//                       value={form.description}
//                       onChange={(e) => set("description", e.target.value)}
//                       rows={4}
//                     />
//                   ) : (
//                     <p className="text-sm text-gray-600">{caseData?.description || "No description provided."}</p>
//                   )}
//                 </div>
//               </div>
//             </TabsContent>

//             {/* ── NOTES TAB ── */}
//             <TabsContent value="notes" className="space-y-4">
//               {/* Add note input */}
//               <div className="flex gap-2">
//                 <Textarea
//                   placeholder="Add a note..."
//                   value={noteInput}
//                   onChange={(e) => setNoteInput(e.target.value)}
//                   rows={2}
//                   className="flex-1"
//                 />
//                 <Button
//                   onClick={handleAddNote}
//                   disabled={addingNote || !noteInput.trim()}
//                   className="self-end"
//                 >
//                   {addingNote ? "Adding..." : "Add Note"}
//                 </Button>
//               </div>

//               {/* Notes list */}
//               {notesLoading ? (
//                 <div className="flex justify-center py-8">
//                   <svg className="animate-spin h-6 w-6 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
//                     <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
//                     <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
//                   </svg>
//                 </div>
//               ) : notes.length === 0 ? (
//                 <p className="text-sm text-gray-400 text-center py-8">No notes yet. Add one above.</p>
//               ) : (
//                 <div className="space-y-3">
//                   {notes.map((note, i) => (
//                     <div
//                       key={note.id ?? i}
//                       className="border rounded-lg p-3 bg-gray-50 space-y-1"
//                     >
//                       <p className="text-sm">{note.content}</p>
//                       <p className="text-xs text-gray-400">
//                         {note.created_at
//                           ? new Date(note.created_at).toLocaleString("en-ZA", {
//                               dateStyle: "medium",
//                               timeStyle: "short",
//                             })
//                           : ""}
//                         {note.is_pinned && (
//                           <span className="ml-2 text-blue-500 font-medium">📌 Pinned</span>
//                         )}
//                       </p>
//                     </div>
//                   ))}
//                 </div>
//               )}
//             </TabsContent>

//             {/* ── DOCUMENTS TAB ── */}
//             <TabsContent value="documents" className="space-y-4">
//               <div className="flex justify-end">
//                 <Button size="sm" onClick={() => setShowUploadModal(true)}>
//                   + Upload Document
//                 </Button>
//               </div>
//               <DocumentsList caseId={caseId} />
//               <UploadDocumentModal
//                 open={showUploadModal}
//                 onOpenChange={setShowUploadModal}
//                 caseId={caseId}
//               />
//             </TabsContent>
//           </Tabs>
//         )}
//       </DialogContent>
//     </Dialog>
//   );
// }

// export default ViewCaseModal;


// "use client"

// import { useEffect, useState } from "react"
// import {
//   Dialog,
//   DialogContent,
//   DialogHeader,
//   DialogTitle
// } from "@/components/ui/dialog"
// import { Button } from "@/components/ui/button"
// import { Label } from "@/components/ui/label"
// import { Input } from "@/components/ui/input"
// import { Textarea } from "@/components/ui/textarea"
// import {
//   Select,
//   SelectContent,
//   SelectItem,
//   SelectTrigger,
//   SelectValue,
// } from "@/components/ui/select"
// import { DocumentsList } from "./DocumentsList"
// import { 
//   getCaseDetails, 
//   updateCase, 
//   getFirmMembers, 
//   getAllMatterTypes, 
//   assignToCase 
// } from "../../lib/api/cases"
// import { UploadDocumentModal } from "./UploadDocumentModal"
// import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
// import { getCaseNotes } from "../../lib/api/cases"
// import { addNote } from "../../lib/api/cases"

// export function ViewCaseModal({ open, onOpenChange, caseId }) {
//   const [caseData, setCaseData] = useState(null)
//   const [loading, setLoading] = useState(false)
//   const [isEditing, setIsEditing] = useState(false)
//   const [notes, setNotes] = useState([])
//   const [noteInput, setNoteInput] = useState("")
//   const [notesLoading, setNotesLoading] = useState(false)
//   // Initialize with empty strings to avoid uncontrolled→controlled warnings
//   const [form, setForm] = useState({
//     title: "",
//     description: "",
//     status: "",
//     priority: "",
//     matter_type: "",
//       deadline: "", // ✅ ADD THIS
//       notes:","

//   })

//   const [members, setMembers] = useState([])
//   const [matterTypes, setMatterTypes] = useState([])
//   const [selectedUser, setSelectedUser] = useState("")

//   //sate to trigger add documents
//   const [showUploadModal, setShowUploadModal] = useState(false)

//   // Fetch members
//  const fetchNotes = async () => {
//   try {
//     setNotesLoading(true)

//     const res = await getCaseNotes(caseId)

//     const data = res.data || res

//     setNotes(Array.isArray(data) ? data : [])
//   } catch (err) {
//     console.error("Failed to load notes", err)
//   } finally {
//     setNotesLoading(false)
//   }
// }

//   const fetchMembers = async () => {
//   try {
//     const res = await getFirmMembers()

//     console.log("MEMBERS API RESPONSE:", res) // ✅ THIS

//     setMembers(Array.isArray(res) ? res : res.data || [])
//   } catch (err) {
//     console.error("Failed to load members", err)
//   }
// }

//   // Fetch matter types
//   const fetchMatterTypes = async () => {
//     try {
//       const res = await getAllMatterTypes()
//       setMatterTypes(res.data || [])
//     } catch (err) {
//       console.error("Failed to load matter types", err)
//     }
//   }

//   // Fetch case details
//   const fetchCase = async () => {
//     try {
//       setLoading(true)
//       const res = await getCaseDetails(caseId)
//       const data = res.data || res
//       setCaseData(data)
//     } catch (err) {
//       console.error("Failed to load case", err)
//     } finally {
//       setLoading(false)
//     }
//   }

//   // Load data when modal opens
//   useEffect(() => {
//     if (open) {
//       fetchMembers()
//       fetchMatterTypes()
//       if (caseId) {
//         fetchCase()
//           fetchNotes()

//       }
//     }
//   }, [open, caseId])

//   //add notes
//   const handleAddNote = async () => {
//   try {
//     if (!noteInput.trim()) return

//     await addNote(caseId, {
//       content: noteInput,
//       is_pinned: false
//     })

//     setNoteInput("")

//     await fetchNotes()
//   } catch (err) {
//     console.error("Failed to add note", err)
//   }
// }

//   // Populate form when caseData loads
// useEffect(() => {
//   if (caseData) {
//     setForm({
//       title: caseData.title || "",
//       description: caseData.description || "",
//       status: caseData.status || "",
//       priority: caseData.priority || "",
//       matter_type: caseData.matter_type?.id?.toString() || "",
//       deadline: caseData.deadline
//         ? caseData.deadline.split("T")[0]
//         : "",
//     })
//   }
// }, [caseData])


// useEffect(() => {
//   if (caseData?.assigned_lawyer) {
//     setSelectedUser(caseData.assigned_lawyer.id.toString())
//   }
// }, [caseData])

//   // Update form field
//   const set = (key, value) => {
//     setForm(prev => ({ ...prev, [key]: value }))
//   }

//   // Save changes
//   const handleSave = async () => {
//     try {
//       // Update case fields
//         const payload = {
//   title: form.title,
//   description: form.description,
//   status: form.status,
//   priority: form.priority,
// }

// if (form.matter_type) {
//   payload.matter_type = Number(form.matter_type)
// }

// if (form.deadline) {
//   payload.deadline = form.deadline
// }

// await updateCase(caseId, payload)
//       // await updateCase(caseId, {
//       //   ...form,
//       //   matter_type: form.matter_type ? Number(form.matter_type) : null,
//       // })

//       // Assign user if selected
//       if (selectedUser) {
//         // await assignToCase(caseId, Number(selectedUser))
//         await assignToCase(caseId, {
//   user_id: Number(selectedUser)
// })
//       }

//       setIsEditing(false)
//       fetchCase()
//     } catch (err) {
//       console.error("Update failed", err)
//     }
//   }

//   if (!caseId) return null

//   return (
//     <Dialog open={open} onOpenChange={onOpenChange}>
//       <DialogContent className="sm:max-w-[900px]">
        
//         {/* <DialogHeader className="flex flex-row justify-between items-center">
//           <DialogTitle>Case Details</DialogTitle>
//           <Button
//             variant="outline"
//             size="sm"
//             onClick={() => setIsEditing(!isEditing)}
//           >
//             {isEditing ? "Cancel" : "Edit"}
//           </Button>
//         </DialogHeader> */}
//         <DialogHeader className="flex flex-row justify-between items-center">
//   <DialogTitle>Case Details</DialogTitle>

//   <div className="flex gap-2">
//     <Button
//       variant="outline"
//       size="sm"
//       onClick={() => setIsEditing(!isEditing)}
//     >
//       {isEditing ? "Cancel" : "Edit"}
//     </Button>

//     {/* <Button
//       size="sm"
//       onClick={() => setShowUploadModal(true)}
//     >
//       Upload
//     </Button> */}
//   </div>
// </DialogHeader>

// <Tabs defaultValue="details">

//   <TabsList>
//     <TabsTrigger value="details">Details</TabsTrigger>
//     <TabsTrigger value="documents">Documents</TabsTrigger>
//     <TabsTrigger value="notes">Notes</TabsTrigger>
//   </TabsList>

//   {/* ================= DETAILS TAB ================= */}
//   <TabsContent value="details">

//         {loading ? (
//           <p className="text-sm text-gray-500">Loading...</p>
//         ) : !caseData ? (
//           <p className="text-sm text-gray-500">No data</p>
//         ) : (
//           <div className="grid grid-cols-2 gap-4 text-sm">
            
//             {/* TITLE */}
//             <div>
//               <Label>Title</Label>
//               <Input
//                 value={form.title}
//                 disabled={!isEditing}
//                 onChange={(e) => set("title", e.target.value)}
//               />
//             </div>

//             {/* CLIENT */}
//             <div>
//               <Label>Client</Label>
//               <Input 
//                 value={`${caseData?.client?.first_name || ""} ${caseData?.client?.last_name || ""}`.trim()} 
//                 disabled 
//               />
//             </div>

//             {/* MATTER TYPE */}
//             <div>
//               <Label>Matter Type</Label>
//               <Select
//                 value={form.matter_type}
//                 onValueChange={(v) => set("matter_type", v)}
//                 disabled={!isEditing}
//               >
//                 <SelectTrigger>
//                   <SelectValue placeholder="Select matter type" />
//                 </SelectTrigger>
//                 <SelectContent>
//                   {matterTypes.map((mt) => (
//                     <SelectItem key={mt.id} value={mt.id.toString()}>
//                       {mt.name}
//                     </SelectItem>
//                   ))}
//                 </SelectContent>
//               </Select>
//             </div>

//             {/* STATUS */}
//             <div>
//               <Label>Status</Label>
//               <Select
//                 value={form.status}
//                 onValueChange={(v) => set("status", v)}
//                 disabled={!isEditing}
//               >
//                 <SelectTrigger>
//                   <SelectValue placeholder="Select status" />
//                 </SelectTrigger>
//                 <SelectContent>
//                   <SelectItem value="new">New</SelectItem>
//                   <SelectItem value="active">Active</SelectItem>
//                   <SelectItem value="on_hold">On Hold</SelectItem>
//                   <SelectItem value="closed">Closed</SelectItem>
//                 </SelectContent>
//               </Select>
//             </div>

//             {/* PRIORITY */}
//             <div>
//               <Label>Priority</Label>
//               <Select
//                 value={form.priority}
//                 onValueChange={(v) => set("priority", v)}
//                 disabled={!isEditing}
//               >
//                 <SelectTrigger>
//                   <SelectValue placeholder="Select priority" />
//                 </SelectTrigger>
//                 <SelectContent>
//                   <SelectItem value="low">Low</SelectItem>
//                   <SelectItem value="medium">Medium</SelectItem>
//                   <SelectItem value="high">High</SelectItem>
//                   <SelectItem value="urgent">Urgent</SelectItem>
//                 </SelectContent>
//               </Select>
//             </div>

//             {/* ASSIGN LAWYER/ASSISTANT */}
//             <div>
//               <Label>Assign Lawyer / Assistant</Label>
//               <Select
//                 // value={selectedUser}
//                 // onValueChange={(v) => setSelectedUser(v)}
//                 value={selectedUser?.toString() || ""}
//               onValueChange={(v) => setSelectedUser(v)}
//                 disabled={!isEditing}
//               >
//                 <SelectTrigger>
//                   <SelectValue placeholder="Select user" />
//                 </SelectTrigger>
//                 <SelectContent>
//                   {members.map((m) => (
//                     <SelectItem key={m.id} value={m.id.toString()}>
//                       {m.name} ({m.role})
//                     </SelectItem>
//                   ))}
//                 </SelectContent>
//               </Select>
//             </div>

//             {/* DEADLINE */}
//             <div>
//               <Label>Deadline</Label>
//               <Input
//   type="date"
//   value={form.deadline || ""}
//   disabled={!isEditing}
//   onChange={(e) => set("deadline", e.target.value)}
// />
//               {/* <Input
//                 value={
//                   caseData.deadline
//                     ? new Date(caseData.deadline).toLocaleDateString()
//                     : ""
//                 }
//                 disabled
//               /> */}
//             </div>

//             {/* REFERENCE */}
//             <div>
//               <Label>Reference</Label>
//               <Input value={caseData.reference_number || ""} disabled />
//             </div>

//             {/* DESCRIPTION - FULL WIDTH */}
//             <div className="col-span-2">
//               <Label>Description</Label>
//               <Textarea
//                 value={form.description}
//                 disabled={!isEditing}
//                 onChange={(e) => set("description", e.target.value)}
//                 rows={4}
//               />
//             </div>
//           </div>
          
//         )}

        
//         <div className="flex justify-end gap-2 mt-4">
//           {isEditing && (
//             <Button onClick={handleSave}>
//               Save Changes
//             </Button>
//           )}

          
//         </div>
//           </TabsContent>

        
        
//                   <UploadDocumentModal
//   open={showUploadModal}
//   onClose={() => setShowUploadModal(false)}
//   caseId={caseId}
// />
//    <TabsContent value="documents">

//     <div className="flex justify-between items-center mb-3">
//       <p className="text-sm font-medium">Documents</p>

//       <Button onClick={() => setShowUploadModal(true)}>
//         Upload Document
//       </Button>
//     </div>

//     <DocumentsList caseId={caseId} />
    

//   </TabsContent>
//   <TabsContent value="notes">
//   <div className="space-y-4">

//     <div>
//       <Label>Add Note</Label>
//       <Textarea
//         value={noteInput}
//         onChange={(e) => setNoteInput(e.target.value)}
//         placeholder="Write an internal case note..."
//         rows={3}
//       />

//       <div className="mt-2 flex justify-end">
//         <Button onClick={handleAddNote}>
//           Add Note
//         </Button>
//       </div>
//     </div>

//     <div className="space-y-3">
//       {notesLoading ? (
//         <p className="text-sm text-gray-500">Loading notes...</p>
//       ) : notes.length === 0 ? (
//         <p className="text-sm text-gray-500">No notes yet</p>
//       ) : (
//         notes.map((note) => (
//           <div
//             key={note.id}
//             className="border rounded-lg p-3"
//           >
//             <p className="text-sm">{note.content}</p>

//             <p className="text-xs text-gray-500 mt-2">
//               {note.created_by_name} •{" "}
//               {new Date(note.created_at).toLocaleString()}
//             </p>
//           </div>
//         ))
//       )}
//     </div>

//   </div>
// </TabsContent>

// </Tabs>


//       </DialogContent>
      
//     </Dialog>
    
//   )
  
// }
