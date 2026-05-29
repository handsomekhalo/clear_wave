"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import backendApi from "../../../../lib/backendApi"
import ClientTopBar from "@/components/client_portal/ClientToBarComponent"

const getAuthHeaders = () => ({
  Authorization: `Token ${localStorage.getItem("authToken")}`,
})

export default function ClientFormPage() {
  const { assignment_id } = useParams()
  const router = useRouter()

  const [templateName, setTemplateName]     = useState("")
  const [submissionId, setSubmissionId]     = useState(null)
  const [formDetails, setFormDetails]       = useState([])  // [{ section, questions: [sq] }]
  const [formAnswers, setFormAnswers]       = useState({})  // { "sectionId-questionId": value }
  const [openAccordions, setOpenAccordions] = useState({})
  const [submittingSection, setSubmittingSection] = useState(null)
  const [loadingAnswers, setLoadingAnswers] = useState(false)
  const [loading, setLoading]               = useState(true)
  const [error, setError]                   = useState(null)
  const [selectedFileUrl, setSelectedFileUrl] = useState(null)
  const [finalSubmitting, setFinalSubmitting] = useState(false)
const [caseId, setCaseId] = useState(null)


  const uploadFile = async (file, caseId) => {
  const formData = new FormData()
  formData.append("file", file)
  formData.append("case", caseId)
  formData.append("name", file.name)

  const res = await backendApi.post(
    `/client_management/client_upload_document/${caseId}/`,
    formData,
    {
      headers: {
        Authorization: `Token ${localStorage.getItem("authToken")}`,
        // no Content-Type — let browser set multipart boundary
      }
    }
  )
  const data = res.data?.data ?? res.data
  return data?.id ?? data?.document_id
}
  // ── init ──────────────────────────────────────────────────────────────────

  useEffect(() => {
    if (!assignment_id) return

    const init = async () => {
      setLoading(true)
      try {
        // 1. Start or resume submission
        const startRes = await backendApi.post(
          `/forms_engine_management/start_form_submission/${assignment_id}/`,
          {},
          { headers: getAuthHeaders() }
        )
        const startData = startRes.data?.data ?? startRes.data
        const sid = startData?.submission_id ?? startData?.id

        setSubmissionId(sid)
        // setCaseId(subData?.assignment?.case_id ?? subData?.assignment?.case)


        // 2. Get template_id + name from submission detail
        const subRes = await backendApi.get(
          `/forms_engine_management/get_form_submission/${assignment_id}/`,
          { headers: getAuthHeaders() }
        )
        const subData = subRes.data?.data ?? subRes.data
        console.log("Submission detail data:", subData)  // Debug log
        const templateId = subData?.assignment?.template_id
        console.log("Template ID:", templateId)  // Debug log

        setTemplateName(subData?.assignment?.template_name ?? "Complete Form")
        setCaseId(subData?.assignment?.case_id ?? subData?.assignment?.case)


        if (!templateId) {
          setError("Could not load form template.")
          return
        }

        // 3. Load sections
        const secRes = await backendApi.get(
          `/forms_engine_management/list_form_sections/${templateId}/`,
          { headers: getAuthHeaders() }
        )
        const secs = secRes.data?.data ?? secRes.data
        const sectionsArray = Array.isArray(secs) ? secs : []

        // 4. Load questions per section
        const sectionsWithQuestions = await Promise.all(
          sectionsArray.map(async (sec) => {
            const sqRes = await backendApi.get(
              `/forms_engine_management/list_section_questions/${templateId}/${sec.id}/`,
              { headers: getAuthHeaders() }
            )
            const sqs = sqRes.data?.data ?? sqRes.data
            return { section: sec, questions: Array.isArray(sqs) ? sqs : [] }
          })
        )
        setFormDetails(sectionsWithQuestions)

        // Open first section by default
        if (sectionsWithQuestions.length > 0) {
          setOpenAccordions({ [sectionsWithQuestions[0].section.id]: true })
        }

        // 5. Load existing answers if resuming
        if (sid) {
          setLoadingAnswers(true)
          try {
            const respRes = await backendApi.get(
              `/forms_engine_management/list_form_responses/${sid}/`,
              { headers: getAuthHeaders() }
            )
            const existing = respRes.data?.data ?? respRes.data
            if (Array.isArray(existing)) {
              const map = {}
           // in the init useEffect, replace the existing answers loop
for (const r of existing) {
  const sectionId = typeof r.section === "object" ? r.section?.id : r.section;
  const questionId = typeof r.question === "object" ? r.question?.id : r.question
  const key = `${sectionId}-${questionId}`

  if (r.response_text != null)         map[key] = r.response_text
  else if (r.response_date)            map[key] = r.response_date
  else if (r.response_number != null)  map[key] = String(r.response_number)
  else if (r.response_boolean != null) map[key] = r.response_boolean ? "checked" : ""
  else if (r.selected_option)          map[key] = r.selected_option.text
}
              setFormAnswers(map)
            }
          } catch (e) {
            // No prior answers — silent skip
          } finally {
            setLoadingAnswers(false)
          }
        }

      } catch (err) {
        console.error("Failed to init form", err)
        setError("Failed to load form. Please try again.")
      } finally {
        setLoading(false)
      }
    }

    init()
  }, [assignment_id])

  // ── accordion ─────────────────────────────────────────────────────────────

  const toggleAccordion = (sectionId) => {
    setOpenAccordions(prev =>
      prev[sectionId] ? {} : { [sectionId]: true }
    )
  }

  // ── answer change ─────────────────────────────────────────────────────────

  const handleInputChange = (sectionId, questionId, value) => {
    setFormAnswers(prev => ({ ...prev, [`${sectionId}-${questionId}`]: value }))
  }

  // ── answer count per section ──────────────────────────────────────────────

  const getSectionAnswerCount = (sectionId) =>
    Object.keys(formAnswers).filter(
      k => k.startsWith(`${sectionId}-`) &&
      typeof formAnswers[k] === "string" &&
      formAnswers[k].trim() !== ""
    ).length

  // ── save section ──────────────────────────────────────────────────────────

  
  const handleSectionSubmit = async (section, questions) => {
    if (submittingSection === section.id || !submissionId) return
    setSubmittingSection(section.id)
    console.log("Submitting section", section.id, "with answers:", formAnswers)  // Debug log

    try {
      for (const sq of questions) {
        const key = `${section.id}-${sq.question.id}`
        const value = formAnswers[key]
        if (value == null || value === "") continue

        const payload = { question: sq.question.id, section: section.id }
        const inputType = sq.question.input_type

if (inputType === "number") {
  payload.response_number = parseFloat(value)
} else if (inputType === "date") {
  payload.response_date = value
} else if (inputType === "yes_no") {
  payload.response_boolean = value === "checked"
} else if (inputType === "checkbox") {
  // value is array of option ids — save each as separate response
  // using response_text to store comma-separated for now
  if (Array.isArray(value) && value.length > 0) {
    payload.response_text = value.join(",")
  } else {
    continue
  }
} else if (inputType === "select") {
  const opt = sq.question.options?.find(o => o.text === value || o.id === value)
  if (opt) payload.selected_option = opt.id
  else payload.response_text = String(value)
} else if (inputType === "file") {
  if (value instanceof File) {
    try {
      // get caseId from submission assignment
      const docId = await uploadFile(value, caseId)
      if (docId) payload.document = docId
      else continue
    } catch (err) {
      console.error("File upload failed", err)
      continue
    }
  } else {
    continue // already uploaded, skip
  }
}


 else {
  payload.response_text = value
}


        await backendApi.post(
          `/forms_engine_management/save_form_response/${submissionId}/`,
          payload,
          { headers: getAuthHeaders() }
        )
      }

      // ── reload answers from backend so UI reflects what was saved ──
// replace the reload block inside handleSectionSubmit
const respRes = await backendApi.get(
  `/forms_engine_management/list_form_responses/${submissionId}/`,
  { headers: getAuthHeaders() }
)
const existing = respRes.data?.data ?? respRes.data
if (Array.isArray(existing)) {
  const map = {}
for (const r of existing) {
  const sectionId = typeof r.section === "object" ? r.section?.id : r.section
  const questionId = typeof r.question === "object" ? r.question?.id : r.question
  const key = `${sectionId}-${questionId}`

  // find the question's input_type from formDetails
  const sq = formDetails
    .flatMap(f => f.questions)
    .find(sq => sq.question.id === questionId)
  const inputType = sq?.question?.input_type

  if (inputType === "checkbox" && r.response_text) {
    // restore as array of numbers
    map[key] = r.response_text.split(",").map(Number)
  } else if (r.response_text != null)         map[key] = r.response_text
  else if (r.response_date)                   map[key] = r.response_date
  else if (r.response_number != null)         map[key] = String(r.response_number)
  else if (r.response_boolean != null)        map[key] = r.response_boolean ? "checked" : ""
  else if (r.selected_option)                 map[key] = r.selected_option.text
  else if (r.document)                        map[key] = r.document.name
}
  setFormAnswers(map)
}
      // Auto-open next section
      const idx = formDetails.findIndex(f => f.section.id === section.id)
      if (idx < formDetails.length - 1) {
        setOpenAccordions({ [formDetails[idx + 1].section.id]: true })
      }

      alert(`Section "${section.name}" saved successfully.`)

    } catch (err) {
      console.error("Section save failed", err)
      alert("Failed to save section. Please try again.")
    } finally {
      setSubmittingSection(null)
      
    }
  }

  // ── final submit ──────────────────────────────────────────────────────────

  const handleFinalSubmit = async () => {
    if (!submissionId) return
    if (!confirm("Once submitted you cannot edit your answers. Continue?")) return

    setFinalSubmitting(true)
    try {
      await backendApi.post(
        `/forms_engine_management/submit_form/${submissionId}/`,
        {},
        { headers: getAuthHeaders() }
      )
      router.push(`/client_portal/forms/${assignment_id}/view`)
    } catch (err) {
      console.error("Final submit failed", err)
      alert("Failed to submit form. Please try again.")
    } finally {
      setFinalSubmitting(false)
    }
  }

  // ── render input — mirrors renderInputField from dynamic_forms ────────────

  const renderInputField = (sq, sectionId) => {
    const q = sq.question
    const key = `${sectionId}-${q.id}`
    const value = formAnswers[key] ?? ""
    const cls = "w-full p-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"

    switch (q.input_type) {
      case "text":
      case "number":
      case "date":
      case "email":
        return (
          <input
            type={q.input_type}
            className={cls}
            value={value}
            onChange={e => handleInputChange(sectionId, q.id, e.target.value)}
            required={sq.is_required}
            placeholder={q.helper_text || ""}
          />
        )

      case "textarea":
        return (
          <textarea
            className={cls}
            rows={4}
            value={value}
            onChange={e => handleInputChange(sectionId, q.id, e.target.value)}
            required={sq.is_required}
            placeholder={q.helper_text || "Enter your response..."}
          />
        )

      case "yes_no":
        return (
          <div className="flex gap-3 mt-1">
            {["Yes", "No"].map(opt => (
              <button
                key={opt}
                type="button"
                onClick={() => handleInputChange(sectionId, q.id, opt === "Yes" ? "checked" : "")}
                className={`px-5 py-2 rounded-lg text-sm font-medium border transition-all ${
                  (opt === "Yes" && value === "checked") || (opt === "No" && value === "")
                    ? "bg-blue-600 text-white border-blue-600"
                    : "bg-white text-gray-600 border-gray-300 hover:border-blue-300"
                }`}
              >
                {opt}
              </button>
            ))}
          </div>
        )

 case "checkbox":
  return (
    <div className="space-y-2 mt-1">
      {q.options?.map(opt => (
        <label key={opt.id} className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={
              Array.isArray(formAnswers[`${sectionId}-${q.id}`])
                ? formAnswers[`${sectionId}-${q.id}`].includes(opt.id)
                : false
            }
            onChange={e => {
              const current = Array.isArray(formAnswers[`${sectionId}-${q.id}`])
                ? formAnswers[`${sectionId}-${q.id}`]
                : []
              const next = e.target.checked
                ? [...current, opt.id]
                : current.filter(id => id !== opt.id)
              handleInputChange(sectionId, q.id, next)
            }}
            className="accent-blue-600"
          />
          <span className="text-sm text-gray-700">{opt.text}</span>
        </label>
      ))}
      {q.options?.length === 0 && (
        <p className="text-xs text-gray-400 italic">No options configured for this question.</p>
      )}
    </div>
  )

      case "select":
        return (
          <select
            className={cls}
            value={value}
            onChange={e => handleInputChange(sectionId, q.id, e.target.value)}
            required={sq.is_required}
          >
            <option value="">Select an option</option>
            {q.options?.map(opt => (
              <option key={opt.id} value={opt.text}>{opt.text}</option>
            ))}
          </select>
        )

     case "file":
  return (
    <div>
      {value && typeof value === "string" && (
        <div className="mb-2 flex items-center gap-2">
          <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
            ✓ Uploaded: {value}
          </span>
        </div>
      )}
      <input
        type="file"
        className={cls}
        onChange={e => {
          const file = e.target.files[0]
          if (file) handleInputChange(sectionId, q.id, file)
        }}
        required={sq.is_required && !value}
      />
    </div>
  )
   

      default:
        return (
          <input
            type="text"
            className={cls}
            value={value}
            onChange={e => handleInputChange(sectionId, q.id, e.target.value)}
            required={sq.is_required}
          />
        )
    }
  }

  // ── loading / error ───────────────────────────────────────────────────────

  if (loading) return (
    <div className="min-h-screen bg-gray-50">
      <ClientTopBar activePage="dashboard" />
      <div className="max-w-3xl mx-auto px-4 py-12 text-center text-sm text-gray-400">
        Loading form...
      </div>
    </div>
  )

  if (error) return (
    <div className="min-h-screen bg-gray-50">
      <ClientTopBar activePage="dashboard" />
      <div className="max-w-3xl mx-auto px-4 py-12 text-center text-sm text-red-500">
        {error}
      </div>
    </div>
  )

  // ── render ────────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-gray-50">
      <ClientTopBar activePage="dashboard" />

      <div className="max-w-3xl mx-auto px-4 py-6 space-y-4">

        {/* Header */}
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <h1 className="text-lg font-semibold text-gray-900">{templateName}</h1>
          <p className="text-sm text-gray-400 mt-1">
            Save each section as you go, then submit when ready.
          </p>
        </div>

        {loadingAnswers && (
          <div className="bg-blue-50 text-blue-700 p-3 rounded-xl border border-blue-200 text-sm">
            ⏳ Loading existing answers...
          </div>
        )}

        {/* Sections */}
        {formDetails.length === 0 ? (
          <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 p-4 rounded-xl text-sm">
            This form has no sections yet. Please contact your lawyer.
          </div>
        ) : (
          <div className="space-y-3">
            {formDetails.map(({ section, questions }) => {
              const answerCount = getSectionAnswerCount(section.id)
              const isOpen = !!openAccordions[section.id]

              return (
                <div key={section.id} className="border border-gray-200 rounded-xl overflow-hidden bg-white">

                  {/* Accordion header */}
                  <button
                    className="w-full text-left px-5 py-4 bg-gray-50 hover:bg-gray-100 flex justify-between items-center transition"
                    onClick={() => toggleAccordion(section.id)}
                  >
                    <div>
                      <h4 className="text-[15px] font-semibold text-gray-800">{section.name}</h4>
                      {section.description && (
                        <p className="text-xs text-gray-500 mt-0.5">{section.description}</p>
                      )}
                      <p className="text-xs text-gray-400 mt-1">
                        {questions.length} question{questions.length !== 1 ? "s" : ""}
                        {answerCount > 0 && (
                          <span className="ml-2 text-green-600 font-medium">
                            ({answerCount} answered)
                          </span>
                        )}
                      </p>
                    </div>
                    <svg
                      className={`w-5 h-5 text-gray-400 transform transition-transform duration-200 ${isOpen ? "rotate-180" : ""}`}
                      fill="none" stroke="currentColor" viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>

                  {/* Accordion content */}
                  {isOpen && (
                    <div className="px-5 py-4 border-t border-gray-100 space-y-4">
                      {questions.length === 0 ? (
                        <p className="text-sm text-gray-400 italic">No questions in this section.</p>
                      ) : (
                        questions.map((sq) => {
                          const key = `${section.id}-${sq.question.id}`
                          const hasAnswer = formAnswers[key] != null && formAnswers[key] !== ""

                          return (
                            <div
                              key={sq.id}
                              className={`p-4 rounded-xl transition ${
                                hasAnswer
                                  ? "bg-green-50 border border-green-200"
                                  : "bg-gray-50 border border-gray-200"
                              }`}
                            >
                              <div className="flex items-start justify-between mb-2">
                                <label className="text-sm font-medium text-gray-800 flex-1">
                                  {sq.question.text}
                                  {sq.is_required && <span className="text-red-500 ml-1">*</span>}
                                  {hasAnswer && (
                                    <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded">
                                      Answered
                                    </span>
                                  )}
                                </label>
                                <span className="ml-3 text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded shrink-0">
                                  {sq.question.input_type}
                                </span>
                              </div>

                              {sq.question.helper_text && (
                                <p className="text-xs text-gray-400 mb-2">{sq.question.helper_text}</p>
                              )}

                              {renderInputField(sq, section.id)}
                            </div>
                          )
                        })
                      )}

                      {/* Save section button */}
                      <div className="pt-3 border-t border-gray-100">
                        <button
                          onClick={() => handleSectionSubmit(section, questions)}
                          disabled={submittingSection === section.id}
                          className={`py-2 px-5 font-semibold rounded-lg text-sm transition shadow ${
                            submittingSection === section.id
                              ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                              : "bg-green-600 hover:bg-green-700 text-white"
                          }`}
                        >
                          {submittingSection === section.id ? "Saving..." : "Save Section"}
                        </button>
                        {answerCount > 0 && (
                          <p className="text-xs text-green-600 mt-2">
                            ✓ {answerCount} answer{answerCount !== 1 ? "s" : ""} ready to save
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}

        {/* Final submit */}
        {formDetails.length > 0 && (
          <div className="bg-white rounded-2xl border border-gray-100 p-5 flex items-center justify-between">
            <p className="text-sm text-gray-400">
              Save each section above, then submit when complete.
            </p>
            <button
              onClick={handleFinalSubmit}
              disabled={finalSubmitting}
              className={`py-2 px-6 font-semibold rounded-xl text-sm text-white transition ${
                finalSubmitting ? "bg-gray-300 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"
              }`}
            >
              {finalSubmitting ? "Submitting..." : "Submit Form"}
             </button>
          </div>
        )}
      </div>

      {/* File preview modal */}
      {selectedFileUrl && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-2xl w-[95%] max-w-4xl p-6 relative">
            <button
              onClick={() => setSelectedFileUrl(null)}
              className="absolute top-3 right-3 text-gray-400 hover:text-gray-700 text-xl"
            >✕</button>
            <p className="text-center font-semibold text-gray-800 mb-4">Document Preview</p>
            <iframe src={selectedFileUrl} title="Document Preview" className="w-full h-[70vh] border rounded-xl" />
            <div className="text-center mt-3">
              <a href={selectedFileUrl} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline text-sm">
                Open in new tab
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
