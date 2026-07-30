import { useEffect, useState } from "react"
import { MoreHorizontal, Pencil, Trash2, Eye } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { UploadDocumentModal } from "./UploadDocumentModal";
import { viewDocument } from "../../lib/api/documents";
import { getDocuments } from "../../lib/api/documents";
import { 
  ChevronLeft, 
  ChevronRight 
} from "lucide-react"
// import { Eye, Pencil } from "lucide-react"
import { updateDocument } from "../../lib/api/documents";


export function EditDocumentForm({ doc, onClose, onSuccess }) {
  const [name, setName] = useState(doc.file_name || "")
  const [description, setDescription] = useState(doc.description || "")
  const [loading, setLoading] = useState(false)
  const [file, setFile] = useState(null)
  

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const formData = new FormData()
      formData.append("file_name", name)
      formData.append("description", description)
      formData.append("category", doc.category)



      if (file) {
        formData.append("file", file)
      }

        console.log("FORM DATA DEBUG:")
  for (let pair of formData.entries()) {
    console.log(pair[0], pair[1])
  }
      await updateDocument(doc.id, formData)

      onSuccess()
    } catch (err) {
      console.error("Update failed", err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">

      <input
        className="w-full border p-2 rounded"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Document name"
      />

      <input
        className="w-full border p-2 rounded"
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
      />

      {file && (
        <p className="text-xs text-gray-500">
          Selected: {file.name}
        </p>
      )}

      <textarea
        className="w-full border p-2 rounded"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Description"
      />

      <div className="flex justify-end gap-2">
        <Button type="button" variant="ghost" onClick={onClose}>
          Cancel
        </Button>

        <Button type="submit" disabled={loading}>
          {loading ? "Saving..." : "Save Changes"}
        </Button>
      </div>
    </form>
  )
}