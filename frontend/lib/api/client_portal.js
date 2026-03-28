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