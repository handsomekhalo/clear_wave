"use client";

import { useEffect, useState } from "react";
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
import {
  getAllClients,
  getAllMatterTypes,
  createClient,
  createMatterType,
  createCase,
  updateCase,
} from "@/lib/api/cases";

const defaultForm = {
  title: "",
  client_id: "",
  case_number: "",
  status: "active",
  assigned_lawyer: "",
  deadline: "",
  description: "",
  matter_type: "",
};

const defaultClient = {
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
};

export default function NewCaseDialog({ open, onOpenChange, onSave, editingCase }) {
  const [form, setForm] = useState(defaultForm);
  const [clients, setClients] = useState([]);
  const [showClientForm, setShowClientForm] = useState(false);
  const [newClient, setNewClient] = useState(defaultClient);
  const [matterTypes, setMatterTypes] = useState([]);
  const [showMatterTypeForm, setShowMatterTypeForm] = useState(false);
  const [newMatterType, setNewMatterType] = useState({ name: "" });

  // ✅ FIX 1: Loading states for all async operations
  const [loadingClients, setLoadingClients] = useState(false);
  const [loadingMatterTypes, setLoadingMatterTypes] = useState(false);
  const [savingClient, setSavingClient] = useState(false);
  const [savingMatterType, setSavingMatterType] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // ✅ FIX 2: Error states
  const [clientError, setClientError] = useState(null);
  const [matterTypeError, setMatterTypeError] = useState(null);
  const [submitError, setSubmitError] = useState(null);

  const fetchClients = async () => {
    setLoadingClients(true);
    try {
      const res = await getAllClients();
      // ✅ FIX 3: Handle both res.data and res directly
      setClients(Array.isArray(res) ? res : res.data ?? []);
    } catch (err) {
      console.error("Failed to load clients", err);
    } finally {
      setLoadingClients(false);
    }
  };

  const fetchMatterTypes = async () => {
    setLoadingMatterTypes(true);
    try {
      const res = await getAllMatterTypes();
      setMatterTypes(Array.isArray(res) ? res : res.data ?? []);
    } catch (err) {
      console.error("Failed to load matter types", err);
    } finally {
      setLoadingMatterTypes(false);
    }
  };

  useEffect(() => {
    if (open) {
      fetchClients();
      fetchMatterTypes();
    }
    if (editingCase) {
      setForm({ ...defaultForm, ...editingCase });
    } else {
      setForm(defaultForm);
    }
    // Reset inline forms on open
    setShowClientForm(false);
    setShowMatterTypeForm(false);
    setNewClient(defaultClient);
    setNewMatterType({ name: "" });
    setClientError(null);
    setMatterTypeError(null);
    setSubmitError(null);
  }, [open, editingCase]);

  const handleCreateClient = async () => {
    if (!newClient.first_name || !newClient.last_name) {
      setClientError("First name and last name are required.");
      return;
    }
    setSavingClient(true);
    setClientError(null);
    try {
      const res = await createClient(newClient);
      // ✅ FIX 4: Safely extract the created client from the response
      const created = res?.data ?? res;
      const clientId = created?.id ?? created?.client_id;

      if (!clientId) throw new Error("Client created but no ID returned");

      // ✅ FIX 5: Add to list and auto-select the new client
      setClients((prev) => [...prev, created]);
      setForm((prev) => ({ ...prev, client_id: clientId }));
      setShowClientForm(false);
      setNewClient(defaultClient);
    } catch (err) {
      console.error("Failed to create client", err);
      setClientError("Failed to save client. Please try again.");
    } finally {
      setSavingClient(false);
    }
  };

  const handleCreateMatterType = async () => {
    if (!newMatterType.name.trim()) {
      setMatterTypeError("Matter type name is required.");
      return;
    }
    setSavingMatterType(true);
    setMatterTypeError(null);
    try {
      const res = await createMatterType({ name: newMatterType.name });
      const created = res?.data ?? res;
      const mtId = created?.id;

      if (!mtId) throw new Error("Matter type created but no ID returned");

      // ✅ FIX 6: Add to list and auto-select the new matter type
      setMatterTypes((prev) => [...prev, created]);
      setForm((prev) => ({ ...prev, matter_type: mtId }));
      setShowMatterTypeForm(false);
      setNewMatterType({ name: "" });
    } catch (err) {
      console.error("Failed to create matter type", err);
      setMatterTypeError("Failed to save matter type. Please try again.");
    } finally {
      setSavingMatterType(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setSubmitError(null);
    try {
      // ✅ FIX 7: Actually call the API and pass result to parent for list refresh
      await onSave(form, editingCase?.id);
      onOpenChange(false);
    } catch (err) {
      console.error("Failed to save case", err);
      setSubmitError("Failed to save case. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[520px] p-0 gap-0 rounded-xl">
        <DialogHeader className="px-6 pt-6 pb-4 border-b border-gray-100">
          <DialogTitle className="text-[16px] font-semibold">
            {editingCase ? "Edit Case" : "New Case"}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
          {/* CLIENT */}
          <div className="space-y-1.5">
            <Label>Client</Label>
            <Select
              value={form.client_id?.toString()}
              onValueChange={(v) => setForm({ ...form, client_id: Number(v) })}
              disabled={loadingClients}
            >
              <SelectTrigger>
                <SelectValue
                  placeholder={loadingClients ? "Loading clients..." : "Select client"}
                />
              </SelectTrigger>
              <SelectContent>
                {/* ✅ FIX 8: Guard against null/undefined id with fallback key */}
                {clients.map((client) => {
                  const id = client.id ?? client.client_id;
                  return (
                    <SelectItem key={String(id ?? `client-${client.email}`)} value={String(id)}>
                      {client.first_name} {client.last_name}
                    </SelectItem>
                  );
                })}
              </SelectContent>
            </Select>

            <button
              type="button"
              className="text-xs text-blue-600 hover:underline"
              onClick={() => setShowClientForm(!showClientForm)}
            >
              {showClientForm ? "− Cancel" : "+ Create New Client"}
            </button>

            {/* Inline new client form */}
            {showClientForm && (
              <div className="border rounded-lg p-3 space-y-3 bg-gray-50">
                <div className="grid grid-cols-2 gap-2">
                  <Input
                    placeholder="First Name"
                    value={newClient.first_name}
                    onChange={(e) => setNewClient({ ...newClient, first_name: e.target.value })}
                  />
                  <Input
                    placeholder="Last Name"
                    value={newClient.last_name}
                    onChange={(e) => setNewClient({ ...newClient, last_name: e.target.value })}
                  />
                </div>
                <Input
                  placeholder="Email"
                  type="email"
                  value={newClient.email}
                  onChange={(e) => setNewClient({ ...newClient, email: e.target.value })}
                />
                <Input
                  placeholder="Phone"
                  value={newClient.phone}
                  onChange={(e) => setNewClient({ ...newClient, phone: e.target.value })}
                />
                {clientError && (
                  <p className="text-xs text-red-500">{clientError}</p>
                )}
                <Button
                  type="button"
                  size="sm"
                  onClick={handleCreateClient}
                  disabled={savingClient}
                >
                  {savingClient ? "Saving..." : "Save Client"}
                </Button>
              </div>
            )}
          </div>

          {/* CASE TITLE */}
          <div className="space-y-1.5">
            <Label>Case Title</Label>
            <Input
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              required
            />
          </div>

          {/* CASE NUMBER (auto-generated, read-only) */}
          <div className="space-y-1.5">
            <Label>Case Number</Label>
            <Input value={form.case_number} disabled placeholder="Auto-generated" />
          </div>

          {/* STATUS */}
          <div className="space-y-1.5">
            <Label>Status</Label>
            <Select
              value={form.status}
              onValueChange={(v) => setForm({ ...form, status: v })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="closed">Closed</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* DEADLINE */}
          <div className="space-y-1.5">
            <Label>Deadline</Label>
            <Input
              type="date"
              value={form.deadline}
              onChange={(e) => setForm({ ...form, deadline: e.target.value })}
            />
          </div>

          {/* MATTER TYPE */}
          <div className="space-y-1.5">
            <Label>Matter Type</Label>
            <Select
              value={form.matter_type?.toString()}
              onValueChange={(v) => setForm({ ...form, matter_type: Number(v) })}
              disabled={loadingMatterTypes}
            >
              <SelectTrigger>
                <SelectValue
                  placeholder={loadingMatterTypes ? "Loading..." : "Select matter type"}
                />
              </SelectTrigger>
              <SelectContent>
                {/* ✅ FIX 9: Safe key using id with fallback to name */}
                {matterTypes.map((mt) => (
                  <SelectItem key={String(mt.id ?? mt.name)} value={String(mt.id)}>
                    {mt.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <button
              type="button"
              className="text-xs text-blue-600 hover:underline"
              onClick={() => setShowMatterTypeForm(!showMatterTypeForm)}
            >
              {showMatterTypeForm ? "− Cancel" : "+ Create New Matter Type"}
            </button>

            {/* Inline new matter type form */}
            {showMatterTypeForm && (
              <div className="border rounded-lg p-3 space-y-2 bg-gray-50">
                <Input
                  placeholder="Matter Type Name"
                  value={newMatterType.name}
                  onChange={(e) => setNewMatterType({ name: e.target.value })}
                />
                {matterTypeError && (
                  <p className="text-xs text-red-500">{matterTypeError}</p>
                )}
                <Button
                  type="button"
                  size="sm"
                  onClick={handleCreateMatterType}
                  disabled={savingMatterType}
                >
                  {savingMatterType ? "Saving..." : "Save Matter Type"}
                </Button>
              </div>
            )}
          </div>

          {/* DESCRIPTION */}
          <div className="space-y-1.5">
            <Label>Description</Label>
            <Textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={3}
            />
          </div>

          {submitError && (
            <p className="text-sm text-red-500">{submitError}</p>
          )}

          {/* ACTIONS */}
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={submitting}>
              {submitting
                ? editingCase ? "Updating..." : "Creating..."
                : editingCase ? "Update Case" : "Create Case"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}


// "use client";

// import { useState, useEffect } from "react";
// import {
//   Dialog,
//   DialogContent,
//   DialogHeader,
//   DialogTitle,
// } from "@/components/ui/dialog";
// import { Input } from "@/components/ui/input";
// import { Label } from "@/components/ui/label";
// import { Button } from "@/components/ui/button";
// import { Textarea } from "@/components/ui/textarea";
// import {
//   Select,
//   SelectContent,
//   SelectItem,
//   SelectTrigger,
//   SelectValue,
// } from "@/components/ui/select";

// import {getAllClients} from '../../lib/api/cases'
// import { createClient } from "../../lib/api/cases";
// import { createCase } from "../../lib/api/cases";
// import { getAllMatterTypes } from "../../lib/api/cases";
// import { createMatterType } from "../../lib/api/cases";



// const defaultForm = {
//   title: "",
//   client_id: "",
//   case_number: "",
//   status: "active",
//   assigned_lawyer: "",
//   deadline: "",
//   description: "",
//   matter_type: ""   // ✅ ADD THIS
// }

// const defaultClient = {
//   first_name: "",
//   last_name: "",
//   email: "",
//   phone: "",

// }



// export default function NewCaseDialog({
//   open,
//   onOpenChange,
//   onSave,
//   editingCase
// }) {

//   // const { matterType, loading } = getAllMatterTypes()
  
//   const [form, setForm] = useState(defaultForm)

//   const [clients, setClients] = useState([])

//   const [showClientForm, setShowClientForm] = useState(false)

//   const [newClient, setNewClient] = useState(defaultClient)
// const [matterTypes, setMatterTypes] = useState([])
// const [showMatterTypeForm, setShowMatterTypeForm] = useState(false)
// const [newMatterType, setNewMatterType] = useState({ name: "" })



//   const fetchClients = async () => {

//     try {

//       // const data = await getAllClients()

//       // setClients(data)
//       const res = await getAllClients()
//       setClients(res.data)

//       console.log('all results', res)

//     } catch (err) {

//       console.error("Failed to load clients", err)

//     }

//   }


//   const fetchMatterTypes = async () => {
//   try {
//     const res = await getAllMatterTypes()
//     setMatterTypes(res.data)
//     console.log("matter types", res.data)
//   } catch (err) {
//     console.error("Failed to load matter types", err)
//   }
// }


// const handleCreateMatterType = async () => {
//   try {

//     const res = await createMatterType({
//       name: newMatterType.name   // ✅ must be "name"
//     })

//     const mt = res.data || res

//     setMatterTypes((prev) => [...prev, mt])

//     setForm({ ...form, matter_type: mt.id })

//     setShowMatterTypeForm(false)

//     setNewMatterType({ name: "" })

//   } catch (err) {
//     console.error("Failed to create matter type", err)
//   }
// }
//   //   useEffect(() => {

//   //   if (open) {
//   //     fetchClients()
//   //   }

//   //   if (editingCase) {
//   //     setForm({ ...defaultForm, ...editingCase })
//   //   } else {
//   //     setForm(defaultForm)
//   //   }

//   // }, [open, editingCase])
//   useEffect(() => {

//   if (open) {
//     fetchClients()
//     fetchMatterTypes() // ✅ ADD THIS
//   }

//   if (editingCase) {
//     setForm({ ...defaultForm, ...editingCase })
//   } else {
//     setForm(defaultForm)
//   }

// }, [open, editingCase])


//   const handleCreateClient = async () => {

//     try {

//       const client = await createClient(newClient)

//       setClients((prev) => [...prev, client])

//       setForm({ ...form, client_id: client.id })

//       setShowClientForm(false)

//       setNewClient(defaultClient)

//     } catch (err) {

//       console.error("Failed to create client", err)

//     }

//   }


//   const handleSubmit = (e) => {

//     e.preventDefault()

//     onSave(form, editingCase?.id)

//   }


//   return (

//     <Dialog open={open} onOpenChange={onOpenChange}>

//       <DialogContent className="sm:max-w-[520px] p-0 gap-0 rounded-xl">

//         <DialogHeader className="px-6 pt-6 pb-4 border-b border-gray-100">

//           <DialogTitle className="text-[16px] font-semibold">

//             {editingCase ? "Edit Case" : "New Case"}

//           </DialogTitle>

//         </DialogHeader>


//         <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">

//           {/* CLIENT SELECT */}

//           <div className="space-y-1.5">

//             <Label>Client</Label>

//             <Select
//   disabled={clients.length === 0}
//   value={form.client_id?.toString()}
//   onValueChange={(v) =>
//     // setForm({ ...form, client_id: v })
//   // setForm({ ...form, client_id: v })
//   setForm({ ...form, client_id: Number(v) })
//   }
// >

//               <SelectTrigger>
//                 <SelectValue placeholder="Select client" />
//               </SelectTrigger>

//               <SelectContent>
//                 {clients.map((client) => {

//   const id = client.id || client.client_id

//   return (
//     <SelectItem
//       key={id}
//       value={id?.toString()}
//     >
//       {client.first_name} {client.last_name}
//     </SelectItem>
//   )

// })}

            

//               </SelectContent>

//             </Select>

//             <button
//               type="button"
//               className="text-xs text-blue-600"
//               onClick={() =>
//                 setShowClientForm(!showClientForm)
//               }
//             >
//               + Create New Client
//             </button>

//           </div>


//           {/* CLIENT CREATION FORM */}

//           {showClientForm && (

//             <div className="border rounded-lg p-3 space-y-3 bg-gray-50">

//               <Input
//                 placeholder="First Name"
//                 value={newClient.first_name}
//                 onChange={(e) =>
//                   setNewClient({
//                     ...newClient,
//                     first_name: e.target.value
//                   })
//                 }
//               />

//               <Input
//                 placeholder="Last Name"
//                 value={newClient.last_name}
//                 onChange={(e) =>
//                   setNewClient({
//                     ...newClient,
//                     last_name: e.target.value
//                   })
//                 }
//               />

//               <Input
//                 placeholder="Email"
//                 value={newClient.email}
//                 onChange={(e) =>
//                   setNewClient({
//                     ...newClient,
//                     email: e.target.value
//                   })
//                 }
//               />

//               <Input
//                 placeholder="Phone"
//                 value={newClient.phone}
//                 onChange={(e) =>
//                   setNewClient({
//                     ...newClient,
//                     phone: e.target.value
//                   })
//                 }
//               />

               

//               <Button
//                 type="button"
//                 size="sm"
//                 onClick={handleCreateClient}
//               >
//                 Save Client
//               </Button>

//             </div>

//           )}


//           {/* CASE TITLE */}

//           <div className="space-y-1.5">

//             <Label>Case Title</Label>

//             <Input
//               value={form.title}
//               onChange={(e) =>
//                 setForm({
//                   ...form,
//                   title: e.target.value
//                 })
//               }
//               required
//             />

//           </div>


//           {/* CASE NUMBER */}

//           <div className="space-y-1.5">

//             <Label>Case Number</Label>

//             <Input
//               value={form.case_number}
//               onChange={(e) =>
//                 setForm({
//                   ...form,
//                   case_number: e.target.value
//                 })
//               }
//               disabled
//             />

            
//           </div>


//           {/* STATUS */}

//           <div className="space-y-1.5">

//             <Label>Status</Label>

//             <Select
//               value={form.status}
//               onValueChange={(v) =>
//                 setForm({ ...form, status: v })
//               }
//             >

//               <SelectTrigger>
//                 <SelectValue />
//               </SelectTrigger>

//               <SelectContent>

//                 <SelectItem value="active">Active</SelectItem>

//                 <SelectItem value="pending">Pending</SelectItem>

//                 <SelectItem value="closed">Closed</SelectItem>

//               </SelectContent>

//             </Select>

//           </div>


//           {/* DEADLINE */}

//           <div className="space-y-1.5">

//             <Label>Deadline</Label>

//             <Input
//               type="date"
//               value={form.deadline}
//               onChange={(e) =>
//                 setForm({
//                   ...form,
//                   deadline: e.target.value
//                 })
//               }
//             />


          

//           </div>

//           {/*mMatter Type*/}
//           <div className="space-y-1.5">

//   <Label>Matter Type</Label>

//   <Select
//     value={form.matter_type?.toString()}
//     onValueChange={(v) =>
//       setForm({ ...form, matter_type: Number(v) })
//     }
//   >

//     <SelectTrigger>
//       <SelectValue placeholder="Select matter type" />
//     </SelectTrigger>

//     <SelectContent>

//       {matterTypes.map((mt) => (
//         <SelectItem
//           key={mt.id}
//           value={mt.id.toString()}
//         >
//           {mt.name}
//         </SelectItem>
//       ))}

//     </SelectContent>

//   </Select>

//   <button
//     type="button"
//     className="text-xs text-blue-600"
//     onClick={() => setShowMatterTypeForm(!showMatterTypeForm)}
//   >
//     + Create New Matter Type
//   </button>

//   {showMatterTypeForm && (
//   <div className="border rounded-lg p-3 space-y-3 bg-gray-50">

//     <Input
//       placeholder="Matter Type Name"
//       value={newMatterType.name}
//       onChange={(e) =>
//         setNewMatterType({ name: e.target.value })
//       }
//     />

//     <Button
//       type="button"
//       size="sm"
//       onClick={handleCreateMatterType}
//     >
//       Save Matter Type
//     </Button>

//   </div>
// )}

// </div>
          


//           {/* DESCRIPTION */}

//           <div className="space-y-1.5">

//             <Label>Description</Label>

//             <Textarea
//               value={form.description}
//               onChange={(e) =>
//                 setForm({
//                   ...form,
//                   description: e.target.value
//                 })
//               }
//             />

//           </div>


//           {/* ACTIONS */}

//           <div className="flex justify-end gap-2 pt-2">

//             <Button
//               type="button"
//               variant="ghost"
//               onClick={() => onOpenChange(false)}
//             >
//               Cancel
//             </Button>

//             <Button type="submit">

//               {editingCase
//                 ? "Save Changes"
//                 : "Create Case"}

//             </Button>

//           </div>

//         </form>

//       </DialogContent>

//     </Dialog>

//   )

// }
