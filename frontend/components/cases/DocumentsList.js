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
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { UploadDocumentModal } from "./UploadDocumentModal";
import { viewDocument } from "../../lib/api/documents";
import { getDocuments } from "../../lib/api/documents";

export function DocumentsList({ caseId }) {
  const [docs, setDocs] = useState([])
  const [showUpload, setShowUpload] = useState(false)


  useEffect(() => {
  const fetchDocs = async () => {
    try {
      const res = await getDocuments(caseId)
      setDocs(res.data || res)
    } catch (err) {
      console.error("Failed to load documents", err)
    }
  }

  fetchDocs()
}, [caseId])

const handleView = async (doc) => {
  const res = await viewDocument(doc.id)
  window.open(res.url, "_blank")
}
// const handleView = async (doc) => {
//   const res = await viewDocument(doc.id)

//   window.open(res.url, "_blank") // 🔥 opens file securely
// }

  return (
    <>
      <div className="flex justify-between mb-4">
        <h3>Documents</h3>
        {/* {documents.length === 0 && ( */}
          {docs.length === 0 && (
  <p className="text-sm text-gray-500">
    No documents uploaded yet
  </p>
)}
        <Button onClick={() => setShowUpload(true)}>
          + Add Document
        </Button>
      </div>
      

      <Table>
        <TableHeader>
            
        {docs.map(doc => (
            
        <TableRow key={doc.id}>
          <TableHead>File Name</TableHead>
           <TableHead>Uploaded By</TableHead>
            <TableHead>Date</TableHead>
            <TableHead>Actions</TableHead>

  <TableCell>{doc.file_name}</TableCell>
  <TableCell>{doc.created_at}</TableCell>
  <TableCell>
    {/* <Button size="sm" onClick={() => handleView(doc)}>
      View
    </Button> */}
    <Button size="sm" onClick={() => handleView(doc)}>
  View
</Button>
  </TableCell>
</TableRow>
        ))}


        </TableHeader>
      </Table>

      <UploadDocumentModal 
        open={showUpload}
        onClose={() => setShowUpload(false)}
        caseId={caseId}
      />
    </>
  )
}