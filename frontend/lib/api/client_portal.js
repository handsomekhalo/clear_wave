import backendApi from "@/utils/backendApi";



export const getClientCaseDetail = async (caseId) => {
  const token = localStorage.getItem("authToken")

  const res = await backendApi.get(
    `/client_management/client_case_detail/${caseId}/`,
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  )

  console.log('res.data.data', res)

  return res.data.data
}



export const getCaseMessages = async (caseId) => {
  const token = localStorage.getItem("authToken")

  const res = await backendApi.get(
    `/client_management/list_case_messages/${caseId}/`,
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  )

  return res.data.data
}

export const getClientCases = async () => {
  const token = localStorage.getItem("authToken")

  const res = await backendApi.get(
    `/client_management/list_client_cases/`,
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  )

  return res.data
}

export const getClientDocuments = async (caseId) => {
  const token = localStorage.getItem("authToken")

  const res = await backendApi.get(
    `/client_management/list_client_documents/${caseId}/`,
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  )

  console.log("DOCUMENT API RESPONSE:", res.data)

  return res.data   // ✅ IMPORTANT
}


export const viewDocument = async (documentId) => {
  const token = localStorage.getItem("authToken") // ✅ FIX

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

// export const viewDocument = async (documentId) => {
//   const token = localStorage.getItem("token")

//   const res = await backendApi.get(
//     `/document_management/view_document/${documentId}/`,
//     {
//       headers: {
//         Authorization: `Token ${token}`
//       }
//     }
//   )

//   return res.data
// }


// export const getClientDocuments = async (caseId) => {
//   const token = localStorage.getItem("authToken")

//   const res = await backendApi.get(
//     `/client_management/list_client_documents/${caseId}/`,
//     {
//       headers: {
//         Authorization: `Token ${token}`
//       }
//     }
//   )

//   return res.data.data
// }
// export const getClientCases = async () => {
//   const token = localStorage.getItem("authToken")

//   const res = await backendApi.get(
//     `/client_management/list_client_cases/`,
//     {
//       headers: {
//         Authorization: `Token ${token}`
//       }
//     }
//   )

//   return res.data.data
// }