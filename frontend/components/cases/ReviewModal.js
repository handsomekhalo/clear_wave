"use client";

// ─────────────────────────────────────────────────────────────────────────────
// ReviewModal.js  —  drop-in replacement for the review drawer
// Place at: frontend/components/cases/ReviewModal.js
// ─────────────────────────────────────────────────────────────────────────────
// In ViewCaseModal.js:
//   1. Import this component:
//        import ReviewModal from "./ReviewModal";
//
//   2. Remove the entire createPortal block (the {reviewingAssignment && createPortal(...)})
//
//   3. Add this just before the closing </> of the return:
//        <ReviewModal
//          open={!!reviewingAssignment}
//          assignment={reviewingAssignment}
//          caseData={caseData}
//          submission={submission}
//          responses={responses}
//          reviewLoading={reviewLoading}
//          reviewError={reviewError}
//          reviewNotes={reviewNotes}
//          setReviewNotes={setReviewNotes}
//          submitting={submitting}
//          onReview={handleReview}
//          onClose={() => {
//            setReviewingAssignment(null);
//            setSubmission(null);
//            setResponses([]);
//            setReviewError(null);
//          }}
//          renderAnswer={renderAnswer}
//          responsesBySection={responsesBySection}
//        />
//
//   4. Keep handleOpenReview exactly as it was originally (no onOpenChange calls needed).
//      Keep handleReview exactly as it was originally too.
//      Remove the drawerOpen state if you added it.
// ─────────────────────────────────────────────────────────────────────────────

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { CheckCircle, XCircle } from "lucide-react";

const FORM_STATUS_STYLES = {
  pending:      "bg-gray-100 text-gray-600",
  in_progress:  "bg-blue-100 text-blue-700",
  submitted:    "bg-yellow-100 text-yellow-700",
  under_review: "bg-orange-100 text-orange-700",
  approved:     "bg-green-100 text-green-700",
  rejected:     "bg-red-100 text-red-700",
};

export default function ReviewModal({
  open,
  assignment,
  caseData,
  submission,
  responses,
  reviewLoading,
  reviewError,
  reviewNotes,
  setReviewNotes,
  submitting,
  onReview,
  onClose,
  renderAnswer,
  responsesBySection,
}) {
  if (!assignment) return null;

  return (
    <Dialog open={open} onOpenChange={(val) => { if (!val) onClose(); }}>
      <DialogContent className="sm:max-w-[640px] max-h-[85vh] flex flex-col p-0 gap-0">

        {/* Header */}
        <DialogHeader className="px-6 py-4 border-b border-slate-200 shrink-0">
          <DialogTitle className="text-base font-semibold">
            {assignment.template?.name}
          </DialogTitle>
          <p className="text-xs text-slate-500 mt-0.5">
            {caseData?.reference_number} ·{" "}
            <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${FORM_STATUS_STYLES[assignment.status] ?? ""}`}>
              {assignment.status_display ?? assignment.status}
            </span>
          </p>
        </DialogHeader>

        {/* Body — scrollable */}
        <div className="flex-1 overflow-y-auto px-6 py-4 min-h-0">
          {reviewLoading ? (
            <div className="py-20 text-center text-slate-400 text-sm">
              Loading submission...
            </div>
          ) : reviewError ? (
            <div className="rounded bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-600">
              {reviewError}
            </div>
          ) : !submission ? (
            <div className="py-20 text-center text-slate-400 text-sm">
              Client has not started this form yet.
            </div>
          ) : (
            <>
              {/* Submission meta */}
              <div className="mb-4 text-xs text-slate-500 space-y-0.5">
                <p>
                  Submitted by:{" "}
                  <span className="font-medium text-slate-700">
                    {submission.submitted_by?.name ?? submission.submitted_by?.email}
                  </span>
                </p>
                {submission.submitted_at && (
                  <p>
                    Submitted at:{" "}
                    <span className="font-medium text-slate-700">
                      {new Date(submission.submitted_at).toLocaleString("en-ZA", {
                        dateStyle: "medium",
                        timeStyle: "short",
                      })}
                    </span>
                  </p>
                )}
                <p>
                  Responses:{" "}
                  <span className="font-medium text-slate-700">
                    {submission.response_count ?? responses.length}
                  </span>
                </p>
              </div>

              {/* Responses accordion */}
              {responses.length === 0 ? (
                <p className="text-sm text-slate-400">No responses recorded.</p>
              ) : (
                <Accordion
                  type="multiple"
                  defaultValue={responsesBySection().map((_, i) => String(i))}
                >
                  {responsesBySection().map((section, i) => (
                    <AccordionItem key={i} value={String(i)}>
                      <AccordionTrigger>
                        <span className="font-medium">{section.label}</span>
                        <span className="ml-2 text-xs text-slate-400">
                          {section.responses.length} answers
                        </span>
                      </AccordionTrigger>
                      <AccordionContent>
                        <div className="space-y-4 pt-2">
                          {section.responses.map((r) => (
                            <div key={r.id}>
                              <p className="text-xs font-medium text-slate-600 mb-1">
                                {r.question?.text}
                                {r.question?.input_type && (
                                  <span className="ml-2 text-slate-400 font-normal">
                                    [{r.question.input_type}]
                                  </span>
                                )}
                              </p>
                              <div className="bg-slate-50 border border-slate-200 rounded px-3 py-2 text-sm text-slate-800">
                                {renderAnswer(r)}
                              </div>
                            </div>
                          ))}
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              )}

              {/* Previous review notes */}
              {assignment.review_notes && (
                <div className="mt-4 rounded bg-yellow-50 border border-yellow-200 px-4 py-3">
                  <p className="text-xs font-medium text-yellow-800 mb-1">
                    Previous Review Notes
                  </p>
                  <p className="text-sm text-yellow-900">{assignment.review_notes}</p>
                  {assignment.reviewed_by && (
                    <p className="text-xs text-yellow-700 mt-1">
                      — {assignment.reviewed_by.name},{" "}
                      {assignment.reviewed_at
                        ? new Date(assignment.reviewed_at).toLocaleDateString("en-ZA")
                        : ""}
                    </p>
                  )}
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer — approve / reject */}
        {submission?.is_complete && (
          <div className="px-6 py-4 border-t border-slate-200 space-y-3 shrink-0">
            {reviewError && (
              <p className="text-xs text-red-600">{reviewError}</p>
            )}
            <div>
              <Label className="text-xs mb-1 block">Review Notes</Label>
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
                onClick={() => onReview("rejected")}
                disabled={submitting}
              >
                <XCircle className="mr-1.5 h-3.5 w-3.5" />
                {submitting ? "Saving..." : "Reject"}
              </Button>
              <Button
                size="sm"
                className="bg-green-600 hover:bg-green-700 text-white"
                onClick={() => onReview("approved")}
                disabled={submitting}
              >
                <CheckCircle className="mr-1.5 h-3.5 w-3.5" />
                {submitting ? "Saving..." : "Approve"}
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}