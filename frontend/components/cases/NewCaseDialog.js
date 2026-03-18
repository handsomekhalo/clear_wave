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

import {getAllClients} from '../../lib/api/cases'
import { createClient } from "../../lib/api/cases";
import { createCase } from "../../lib/api/cases";
import { getAllMatterTypes } from "../../lib/api/cases";
import { createMatterType } from "../../lib/api/cases";



const defaultForm = {
  title: "",
  client_id: "",
  case_number: "",
  status: "active",
  assigned_lawyer: "",
  deadline: "",
  description: "",
  matter_type: ""   // ✅ ADD THIS
}

const defaultClient = {
  first_name: "",
  last_name: "",
  email: "",
  phone: "",

}



export default function NewCaseDialog({
  open,
  onOpenChange,
  onSave,
  editingCase
}) {

  // const { matterType, loading } = getAllMatterTypes()
  
  const [form, setForm] = useState(defaultForm)

  const [clients, setClients] = useState([])

  const [showClientForm, setShowClientForm] = useState(false)

  const [newClient, setNewClient] = useState(defaultClient)
const [matterTypes, setMatterTypes] = useState([])
const [showMatterTypeForm, setShowMatterTypeForm] = useState(false)
const [newMatterType, setNewMatterType] = useState({ name: "" })



  const fetchClients = async () => {

    try {

      // const data = await getAllClients()

      // setClients(data)
      const res = await getAllClients()
      setClients(res.data)

      console.log('all results', res)

    } catch (err) {

      console.error("Failed to load clients", err)

    }

  }


  const fetchMatterTypes = async () => {
  try {
    const res = await getAllMatterTypes()
    setMatterTypes(res.data)
    console.log("matter types", res.data)
  } catch (err) {
    console.error("Failed to load matter types", err)
  }
}


const handleCreateMatterType = async () => {
  try {

    const res = await createMatterType({
      name: newMatterType.name   // ✅ must be "name"
    })

    const mt = res.data || res

    setMatterTypes((prev) => [...prev, mt])

    setForm({ ...form, matter_type: mt.id })

    setShowMatterTypeForm(false)

    setNewMatterType({ name: "" })

  } catch (err) {
    console.error("Failed to create matter type", err)
  }
}
  //   useEffect(() => {

  //   if (open) {
  //     fetchClients()
  //   }

  //   if (editingCase) {
  //     setForm({ ...defaultForm, ...editingCase })
  //   } else {
  //     setForm(defaultForm)
  //   }

  // }, [open, editingCase])
  useEffect(() => {

  if (open) {
    fetchClients()
    fetchMatterTypes() // ✅ ADD THIS
  }

  if (editingCase) {
    setForm({ ...defaultForm, ...editingCase })
  } else {
    setForm(defaultForm)
  }

}, [open, editingCase])


  const handleCreateClient = async () => {

    try {

      const client = await createClient(newClient)

      setClients((prev) => [...prev, client])

      setForm({ ...form, client_id: client.id })

      setShowClientForm(false)

      setNewClient(defaultClient)

    } catch (err) {

      console.error("Failed to create client", err)

    }

  }


  const handleSubmit = (e) => {

    e.preventDefault()

    onSave(form, editingCase?.id)

  }


  return (

    <Dialog open={open} onOpenChange={onOpenChange}>

      <DialogContent className="sm:max-w-[520px] p-0 gap-0 rounded-xl">

        <DialogHeader className="px-6 pt-6 pb-4 border-b border-gray-100">

          <DialogTitle className="text-[16px] font-semibold">

            {editingCase ? "Edit Case" : "New Case"}

          </DialogTitle>

        </DialogHeader>


        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">

          {/* CLIENT SELECT */}

          <div className="space-y-1.5">

            <Label>Client</Label>

            <Select
  disabled={clients.length === 0}
  value={form.client_id?.toString()}
  onValueChange={(v) =>
    // setForm({ ...form, client_id: v })
  // setForm({ ...form, client_id: v })
  setForm({ ...form, client_id: Number(v) })
  }
>

              <SelectTrigger>
                <SelectValue placeholder="Select client" />
              </SelectTrigger>

              <SelectContent>
                {clients.map((client) => {

  const id = client.id || client.client_id

  return (
    <SelectItem
      key={id}
      value={id?.toString()}
    >
      {client.first_name} {client.last_name}
    </SelectItem>
  )

})}

            

              </SelectContent>

            </Select>

            <button
              type="button"
              className="text-xs text-blue-600"
              onClick={() =>
                setShowClientForm(!showClientForm)
              }
            >
              + Create New Client
            </button>

          </div>


          {/* CLIENT CREATION FORM */}

          {showClientForm && (

            <div className="border rounded-lg p-3 space-y-3 bg-gray-50">

              <Input
                placeholder="First Name"
                value={newClient.first_name}
                onChange={(e) =>
                  setNewClient({
                    ...newClient,
                    first_name: e.target.value
                  })
                }
              />

              <Input
                placeholder="Last Name"
                value={newClient.last_name}
                onChange={(e) =>
                  setNewClient({
                    ...newClient,
                    last_name: e.target.value
                  })
                }
              />

              <Input
                placeholder="Email"
                value={newClient.email}
                onChange={(e) =>
                  setNewClient({
                    ...newClient,
                    email: e.target.value
                  })
                }
              />

              <Input
                placeholder="Phone"
                value={newClient.phone}
                onChange={(e) =>
                  setNewClient({
                    ...newClient,
                    phone: e.target.value
                  })
                }
              />

               

              <Button
                type="button"
                size="sm"
                onClick={handleCreateClient}
              >
                Save Client
              </Button>

            </div>

          )}


          {/* CASE TITLE */}

          <div className="space-y-1.5">

            <Label>Case Title</Label>

            <Input
              value={form.title}
              onChange={(e) =>
                setForm({
                  ...form,
                  title: e.target.value
                })
              }
              required
            />

          </div>


          {/* CASE NUMBER */}

          <div className="space-y-1.5">

            <Label>Case Number</Label>

            <Input
              value={form.case_number}
              onChange={(e) =>
                setForm({
                  ...form,
                  case_number: e.target.value
                })
              }
              disabled
            />

            
          </div>


          {/* STATUS */}

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


          {/* DEADLINE */}

          <div className="space-y-1.5">

            <Label>Deadline</Label>

            <Input
              type="date"
              value={form.deadline}
              onChange={(e) =>
                setForm({
                  ...form,
                  deadline: e.target.value
                })
              }
            />


          

          </div>

          {/*mMatter Type*/}
          <div className="space-y-1.5">

  <Label>Matter Type</Label>

  <Select
    value={form.matter_type?.toString()}
    onValueChange={(v) =>
      setForm({ ...form, matter_type: Number(v) })
    }
  >

    <SelectTrigger>
      <SelectValue placeholder="Select matter type" />
    </SelectTrigger>

    <SelectContent>

      {matterTypes.map((mt) => (
        <SelectItem
          key={mt.id}
          value={mt.id.toString()}
        >
          {mt.name}
        </SelectItem>
      ))}

    </SelectContent>

  </Select>

  <button
    type="button"
    className="text-xs text-blue-600"
    onClick={() => setShowMatterTypeForm(!showMatterTypeForm)}
  >
    + Create New Matter Type
  </button>

  {showMatterTypeForm && (
  <div className="border rounded-lg p-3 space-y-3 bg-gray-50">

    <Input
      placeholder="Matter Type Name"
      value={newMatterType.name}
      onChange={(e) =>
        setNewMatterType({ name: e.target.value })
      }
    />

    <Button
      type="button"
      size="sm"
      onClick={handleCreateMatterType}
    >
      Save Matter Type
    </Button>

  </div>
)}

</div>
          


          {/* DESCRIPTION */}

          <div className="space-y-1.5">

            <Label>Description</Label>

            <Textarea
              value={form.description}
              onChange={(e) =>
                setForm({
                  ...form,
                  description: e.target.value
                })
              }
            />

          </div>


          {/* ACTIONS */}

          <div className="flex justify-end gap-2 pt-2">

            <Button
              type="button"
              variant="ghost"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>

            <Button type="submit">

              {editingCase
                ? "Save Changes"
                : "Create Case"}

            </Button>

          </div>

        </form>

      </DialogContent>

    </Dialog>

  )

}
