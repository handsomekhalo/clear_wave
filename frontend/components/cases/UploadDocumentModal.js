import { useEffect, useState } from "react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import {
  Select,

} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"


import { Input } from "@/components/ui/input"

import { uploadDocument } from "../../lib/api/documents"


export function UploadDocumentModal({ open, onClose, caseId }) {
  const [file, setFile] = useState(null)

  // const handleUpload = async () => {
  //   const formData = new FormData()
  //   formData.append('file', file)
  //   formData.append('case_id', caseId)
    
  //   await uploadDocument(formData)
  //   onClose()
  // }
  const handleUpload = async () => {
  const formData = new FormData()

  formData.append("file", file)
  formData.append("category", "other") // or dropdown later
  formData.append("description", "")

  await uploadDocument(caseId, formData)

  onClose()
}

  return (
  
        <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent>
        <DialogTitle>Upload Document</DialogTitle>
        
        <Input 
          type="file" 
          onChange={(e) => setFile(e.target.files[0])}
        />

        <Input placeholder="Document name" />
          <Textarea placeholder="Description (optional)" />
          <Select category />

        <Button onClick={handleUpload}>
          Upload
        </Button>
      </DialogContent>
    </Dialog>
  )
}