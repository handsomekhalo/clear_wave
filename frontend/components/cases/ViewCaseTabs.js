import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ViewCaseModal } from "./ViewCaseModal"
import { DocumentsList } from "./DocumentsList"
import { Button } from "@/components/ui/button"


<ViewCaseModal>
  <Tabs defaultValue="details">
    <TabsList>
      <TabsTrigger value="details">Details</TabsTrigger>
      <TabsTrigger value="documents">Documents</TabsTrigger>
    </TabsList>

    <TabsContent value="details">
      {/* Your existing form */}
    </TabsContent>

    <TabsContent value="documents">
  <div className="flex justify-between items-center mb-2">
    <p className="text-sm font-medium">Documents</p>

    <Button onClick={() => setShowUploadModal(true)}>
      Upload Document
    </Button>
  </div>

  <DocumentsList caseId={caseId} />
</TabsContent>
</Tabs>
</ViewCaseModal>