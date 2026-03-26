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
import { EditDocumentForm } from "./UpdateDocumentModal";


export function DocumentsList({ caseId }) {
  const [docs, setDocs] = useState([])
  const [showUpload, setShowUpload] = useState(false)
  const [viewerOpen, setViewerOpen] = useState(false)
  const [currentDocUrl, setCurrentDocUrl] = useState("")
  const [currentDocName, setCurrentDocName] = useState("")
  const [editOpen, setEditOpen] = useState(false)
const [selectedDoc, setSelectedDoc] = useState(null)
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1)
  const docsPerPage = 5
  
  const totalPages = Math.ceil(docs.length / docsPerPage)
  const startIdx = (currentPage - 1) * docsPerPage
  const endIdx = startIdx + docsPerPage
  const currentDocs = docs.slice(startIdx, endIdx)

  const handleEdit = (doc) => {
  setSelectedDoc(doc)
  setEditOpen(true)
}

  const fetchDocs = async () => {
    try {
      const res = await getDocuments(caseId)
      setDocs(res.data || res)
    } catch (err) {
      console.error("Failed to load documents", err)
    }
  }

    useEffect(() => {
    fetchDocs()
  }, [caseId])


  const handleView = async (doc) => {
    try {
      const res = await viewDocument(doc.id)
      setCurrentDocUrl(res.url)
      setCurrentDocName(doc.file_name)
      setViewerOpen(true)
    } catch (err) {
      console.error("Failed to load document", err)
    }
  }

  const handleUploadSuccess = () => {
    setShowUpload(false)
    fetchDocs()
  }

  return (
    <>
      {/* HEADER */}
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-semibold text-lg">Documents</h3>

        <Button onClick={() => setShowUpload(true)} size="sm">
          {docs.length === 0 ? "Upload Document" : "+ Add Additional Document"}
        </Button>
      </div>

      {/* EMPTY STATE */}
      {docs.length === 0 ? (
        <div className="text-sm text-gray-500 border rounded-lg p-8 text-center">
          <p className="font-medium">No documents uploaded yet</p>
          <p className="text-xs mt-1">Upload your first document to get started</p>
        </div>
      ) : (
        <>
          {/* TABLE */}
          <div className="border rounded-lg overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Uploaded By</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>

              <TableBody>
                {currentDocs.map((doc) => (
                  <TableRow key={doc.id}>
                    <TableCell className="font-medium max-w-[200px] truncate">
                      {doc.file_name}
                    </TableCell>

                    <TableCell className="max-w-[150px] truncate">
                      {doc.description || "-"}
                    </TableCell>

                    <TableCell>
                      {doc.uploaded_by}
                    </TableCell>

                    <TableCell className="text-sm text-gray-500">
                      {new Date(doc.uploaded_at).toLocaleDateString()}
                    </TableCell>

                    <TableCell className="text-right">
                      <div className="flex gap-2 justify-end">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleView(doc)}
                        >
                          View
                        </Button>

                       <Button 
  size="sm" 
  variant="ghost"
  onClick={() => handleEdit(doc)}
>
  Edit
</Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {/* PAGINATION */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4">
              <p className="text-sm text-gray-500">
                Showing {startIdx + 1}-{Math.min(endIdx, docs.length)} of {docs.length} documents
              </p>

              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                >
                  <ChevronLeft className="w-4 h-4" />
                  Previous
                </Button>

                <div className="flex items-center gap-1">
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                    <Button
                      key={page}
                      size="sm"
                      variant={currentPage === page ? "default" : "outline"}
                      onClick={() => setCurrentPage(page)}
                      className="w-8"
                    >
                      {page}
                    </Button>
                  ))}
                </div>

                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                >
                  Next
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </>
      )}

      {/* UPLOAD MODAL */}
      <UploadDocumentModal
        open={showUpload}
        onClose={() => setShowUpload(false)}
        caseId={caseId}
        onSuccess={handleUploadSuccess}
      />

      {/* DOCUMENT VIEWER MODAL */}
      <Dialog open={viewerOpen} onOpenChange={setViewerOpen}>
        <DialogContent className="max-w-4xl h-[75vh]">
          <DialogHeader>
            <DialogTitle>{currentDocName}</DialogTitle>
          </DialogHeader>

          <div className="flex-1 h-full">
            <iframe
              src={currentDocUrl}
              className="w-full h-full border rou"
              title={currentDocName}
            />
          </div>
        </DialogContent>
      </Dialog>
      {/* edit documents*/}
      <Dialog open={editOpen} onOpenChange={setEditOpen}>
  <DialogContent className="max-w-md">
    <DialogHeader>
      <DialogTitle>Edit Document</DialogTitle>
    </DialogHeader>

    {selectedDoc && (
      <EditDocumentForm
        doc={selectedDoc}
        onClose={() => setEditOpen(false)}
        onSuccess={() => {
          setEditOpen(false)
          fetchDocs()
        }}
      />
    )}
  </DialogContent>
</Dialog>
    </>
  )
}

// export function DocumentsList({ caseId }) {
//   const [docs, setDocs] = useState([])
//   const [showUpload, setShowUpload] = useState(false)


//   useEffect(() => {
//   const fetchDocs = async () => {
//     try {
//       const res = await getDocuments(caseId)
//       setDocs(res.data || res)
//     } catch (err) {
//       console.error("Failed to load documents", err)
//     }
//   }

//   fetchDocs()
// }, [caseId])

// const handleView = async (doc) => {
//   const res = await viewDocument(doc.id)
//   window.open(res.url, "_blank")
// }
// // const handleView = async (doc) => {
// //   const res = await viewDocument(doc.id)

// //   window.open(res.url, "_blank") // 🔥 opens file securely
// // }

//   return (
//     <>
//       <div className="flex justify-between mb-4">
//         <h3>Documents</h3>
//         {/* {documents.length === 0 && ( */}
//           {docs.length === 0 && (
//   <p className="text-sm text-gray-500">
//     No documents uploaded yet
//   </p>
// )}
//         <Button onClick={() => setShowUpload(true)}>
//           + Add Document
//         </Button>
//       </div>
      

//       <Table>
//         <TableHeader>
            
//         {docs.map(doc => (
            
//         <TableRow key={doc.id}>
//           <TableHead>File Name</TableHead>
//            <TableHead>Uploaded By</TableHead>
//             <TableHead>Date</TableHead>
//             <TableHead>Actions</TableHead>

//   <TableCell>{doc.file_name}</TableCell>
//   <TableCell>{doc.created_at}</TableCell>
//   <TableCell>
//     {/* <Button size="sm" onClick={() => handleView(doc)}>
//       View
//     </Button> */}
//     <Button size="sm" onClick={() => handleView(doc)}>
//   View
// </Button>
//   </TableCell>
// </TableRow>
//         ))}


//         </TableHeader>
//       </Table>

//       <UploadDocumentModal 
//         open={showUpload}
//         onClose={() => setShowUpload(false)}
//         caseId={caseId}
//       />
//     </>
//   )
// }