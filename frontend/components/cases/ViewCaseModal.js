"use client"

import { useEffect, useState } from "react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { DocumentsList } from "./DocumentsList"
import { 
  getCaseDetails, 
  updateCase, 
  getFirmMembers, 
  getAllMatterTypes, 
  assignToCase 
} from "../../lib/api/cases"
import { UploadDocumentModal } from "./UploadDocumentModal"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"



export function ViewCaseModal({ open, onOpenChange, caseId }) {
  const [caseData, setCaseData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  
  // Initialize with empty strings to avoid uncontrolled→controlled warnings
  const [form, setForm] = useState({
    title: "",
    description: "",
    status: "",
    priority: "",
    matter_type: "",
      deadline: "", // ✅ ADD THIS

  })

  const [members, setMembers] = useState([])
  const [matterTypes, setMatterTypes] = useState([])
  const [selectedUser, setSelectedUser] = useState("")

  //sate to trigger add documents
  const [showUploadModal, setShowUploadModal] = useState(false)

  // Fetch members
 
  const fetchMembers = async () => {
  try {
    const res = await getFirmMembers()

    console.log("MEMBERS API RESPONSE:", res) // ✅ THIS

    setMembers(Array.isArray(res) ? res : res.data || [])
  } catch (err) {
    console.error("Failed to load members", err)
  }
}

  // Fetch matter types
  const fetchMatterTypes = async () => {
    try {
      const res = await getAllMatterTypes()
      setMatterTypes(res.data || [])
    } catch (err) {
      console.error("Failed to load matter types", err)
    }
  }

  // Fetch case details
  const fetchCase = async () => {
    try {
      setLoading(true)
      const res = await getCaseDetails(caseId)
      const data = res.data || res
      setCaseData(data)
    } catch (err) {
      console.error("Failed to load case", err)
    } finally {
      setLoading(false)
    }
  }

  // Load data when modal opens
  useEffect(() => {
    if (open) {
      fetchMembers()
      fetchMatterTypes()
      if (caseId) {
        fetchCase()
      }
    }
  }, [open, caseId])

  // Populate form when caseData loads
useEffect(() => {
  if (caseData) {
    setForm({
      title: caseData.title || "",
      description: caseData.description || "",
      status: caseData.status || "",
      priority: caseData.priority || "",
      matter_type: caseData.matter_type?.id?.toString() || "",
      deadline: caseData.deadline
        ? caseData.deadline.split("T")[0]
        : "",
    })
  }
}, [caseData])


useEffect(() => {
  if (caseData?.assigned_lawyer) {
    setSelectedUser(caseData.assigned_lawyer.id.toString())
  }
}, [caseData])

  // Update form field
  const set = (key, value) => {
    setForm(prev => ({ ...prev, [key]: value }))
  }

  // Save changes
  const handleSave = async () => {
    try {
      // Update case fields
        const payload = {
  title: form.title,
  description: form.description,
  status: form.status,
  priority: form.priority,
}

if (form.matter_type) {
  payload.matter_type = Number(form.matter_type)
}

if (form.deadline) {
  payload.deadline = form.deadline
}

await updateCase(caseId, payload)
      // await updateCase(caseId, {
      //   ...form,
      //   matter_type: form.matter_type ? Number(form.matter_type) : null,
      // })

      // Assign user if selected
      if (selectedUser) {
        // await assignToCase(caseId, Number(selectedUser))
        await assignToCase(caseId, {
  user_id: Number(selectedUser)
})
      }

      setIsEditing(false)
      fetchCase()
    } catch (err) {
      console.error("Update failed", err)
    }
  }

  if (!caseId) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px]">
        
        {/* <DialogHeader className="flex flex-row justify-between items-center">
          <DialogTitle>Case Details</DialogTitle>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsEditing(!isEditing)}
          >
            {isEditing ? "Cancel" : "Edit"}
          </Button>
        </DialogHeader> */}
        <DialogHeader className="flex flex-row justify-between items-center">
  <DialogTitle>Case Details</DialogTitle>

  <div className="flex gap-2">
    <Button
      variant="outline"
      size="sm"
      onClick={() => setIsEditing(!isEditing)}
    >
      {isEditing ? "Cancel" : "Edit"}
    </Button>

    {/* <Button
      size="sm"
      onClick={() => setShowUploadModal(true)}
    >
      Upload
    </Button> */}
  </div>
</DialogHeader>

<Tabs defaultValue="details">

  <TabsList>
    <TabsTrigger value="details">Details</TabsTrigger>
    <TabsTrigger value="documents">Documents</TabsTrigger>
  </TabsList>

  {/* ================= DETAILS TAB ================= */}
  <TabsContent value="details">

        {loading ? (
          <p className="text-sm text-gray-500">Loading...</p>
        ) : !caseData ? (
          <p className="text-sm text-gray-500">No data</p>
        ) : (
          <div className="grid grid-cols-2 gap-4 text-sm">
            
            {/* TITLE */}
            <div>
              <Label>Title</Label>
              <Input
                value={form.title}
                disabled={!isEditing}
                onChange={(e) => set("title", e.target.value)}
              />
            </div>

            {/* CLIENT */}
            <div>
              <Label>Client</Label>
              <Input 
                value={`${caseData?.client?.first_name || ""} ${caseData?.client?.last_name || ""}`.trim()} 
                disabled 
              />
            </div>

            {/* MATTER TYPE */}
            <div>
              <Label>Matter Type</Label>
              <Select
                value={form.matter_type}
                onValueChange={(v) => set("matter_type", v)}
                disabled={!isEditing}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select matter type" />
                </SelectTrigger>
                <SelectContent>
                  {matterTypes.map((mt) => (
                    <SelectItem key={mt.id} value={mt.id.toString()}>
                      {mt.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* STATUS */}
            <div>
              <Label>Status</Label>
              <Select
                value={form.status}
                onValueChange={(v) => set("status", v)}
                disabled={!isEditing}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="new">New</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="on_hold">On Hold</SelectItem>
                  <SelectItem value="closed">Closed</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* PRIORITY */}
            <div>
              <Label>Priority</Label>
              <Select
                value={form.priority}
                onValueChange={(v) => set("priority", v)}
                disabled={!isEditing}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="urgent">Urgent</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* ASSIGN LAWYER/ASSISTANT */}
            <div>
              <Label>Assign Lawyer / Assistant</Label>
              <Select
                // value={selectedUser}
                // onValueChange={(v) => setSelectedUser(v)}
                value={selectedUser?.toString() || ""}
              onValueChange={(v) => setSelectedUser(v)}
                disabled={!isEditing}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select user" />
                </SelectTrigger>
                <SelectContent>
                  {members.map((m) => (
                    <SelectItem key={m.id} value={m.id.toString()}>
                      {m.name} ({m.role})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* DEADLINE */}
            <div>
              <Label>Deadline</Label>
              <Input
  type="date"
  value={form.deadline || ""}
  disabled={!isEditing}
  onChange={(e) => set("deadline", e.target.value)}
/>
              {/* <Input
                value={
                  caseData.deadline
                    ? new Date(caseData.deadline).toLocaleDateString()
                    : ""
                }
                disabled
              /> */}
            </div>

            {/* REFERENCE */}
            <div>
              <Label>Reference</Label>
              <Input value={caseData.reference_number || ""} disabled />
            </div>

            {/* DESCRIPTION - FULL WIDTH */}
            <div className="col-span-2">
              <Label>Description</Label>
              <Textarea
                value={form.description}
                disabled={!isEditing}
                onChange={(e) => set("description", e.target.value)}
                rows={4}
              />
            </div>
          </div>
          
        )}

        
        <div className="flex justify-end gap-2 mt-4">
          {isEditing && (
            <Button onClick={handleSave}>
              Save Changes
            </Button>
          )}

          
        </div>
          </TabsContent>

        
        
                  <UploadDocumentModal
  open={showUploadModal}
  onClose={() => setShowUploadModal(false)}
  caseId={caseId}
/>
   <TabsContent value="documents">

    <div className="flex justify-between items-center mb-3">
      <p className="text-sm font-medium">Documents</p>

      <Button onClick={() => setShowUploadModal(true)}>
        Upload Document
      </Button>
    </div>

    <DocumentsList caseId={caseId} />

  </TabsContent>

</Tabs>


      </DialogContent>
      
    </Dialog>
    
  )
  
}
