// No need for token() or auth() helpers at all
// backendApi interceptor handles it automatically
import backendApi from "../backendApi"


export const getClientCases = async () => {
  const res = await backendApi.get("/client_management/list_client_cases/")
  return res.data?.data ?? res.data
}

export const getCaseMessages = async (caseId) => {
  const res = await backendApi.get(`/client_management/list_case_messages/${caseId}/`)
  return res.data?.data ?? res.data
}

export const sendCaseMessage = async (caseId, content) => {
  const res = await backendApi.post(`/client_management/send_case_message/${caseId}/`, { content })
  return res.data?.data ?? res.data
}

export const getClientCaseDetail = async (caseId) => {
  const res = await backendApi.get(`/client_management/client_case_detail/${caseId}/`)
  return res.data?.data ?? res.data
}

export const getClientDocuments = async (caseId) => {
  const res = await backendApi.get(`/client_management/list_client_documents/${caseId}/`)
  return res.data?.data ?? res.data
}

export const viewDocument = async (documentId) => {
  const res = await backendApi.get(`/document_management/view_document/${documentId}/`)
  return res.data?.data ?? res.data
}

export const getClientFormAssignments = async () => {
  const res = await backendApi.get("/client_management/list_client_form_assignments/")
  return res.data?.data ?? res.data
}