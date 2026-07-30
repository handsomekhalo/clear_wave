import backendApi from "../backendApi"


export const uploadDocument = async (caseId, formData) => {
  const token = localStorage.getItem("token")

  const res = await backendApi.post(
    `/document_management/upload_documents/${caseId}/`, // ✅ include caseId
    formData,
    {
      headers: {
        Authorization: `Token ${token}`,
        "Content-Type": "multipart/form-data",
      },
    }
  )

  return res.data
}


export const getDocuments = async (caseId) => {
  const token = localStorage.getItem("token")

  const res = await backendApi.get(
    `/document_management/get_documents/${caseId}/`,
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  )

  return res.data.data
}



export const viewDocument = async (documentId) => {
  const token = localStorage.getItem("token")

  const res = await backendApi.get(
    `/document_management/view_document/${documentId}/`,
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  )

  return res.data.data
}


export const updateDocument = async (documentId, payload) => {
  const token = localStorage.getItem("token")

  const res = await backendApi.post(
    `/document_management/update_document/${documentId}/`,
    payload,
    {
      headers: {
        Authorization: `Token ${token}`
        // ❌ NO Content-Type
      }
    }
  )

  return res.data.data
}
