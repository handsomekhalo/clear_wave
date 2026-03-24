import backendApi from "@/utils/backendApi";


export const getAllClients = async () => {

  const token = localStorage.getItem("token")

  const res = await backendApi.get("/case_management/get_all_clients", {
    headers: {
      Authorization: `Token ${token}`
    }
  })

  return res.data
}


export const createClient = async (data) => {

  const token = localStorage.getItem("token")

  const res = await backendApi.post("/case_management/create_client/", data, {
    headers: {
      Authorization: `Token ${token}`
    }
  })

  return res.data
}



export const createCase = async (data) => {

  const token = localStorage.getItem("token")

  const res = await backendApi.post("/case_management/create_case/",data, {
    headers: {
      Authorization: `Token ${token}`
    }
  })

  return res.data
}


export const getAllMatterTypes = async () => {

  const token = localStorage.getItem("token")

  const res = await backendApi.get("/case_management/get_all_matter_types/", {
    headers: {
      Authorization: `Token ${token}`
    }
  })
  console.log('weeeeeeeeeeeeeeeeeeeeeeeeeeeeedpfdks[')

  return res.data
}

//get client and case details


export const createMatterType = async (data) => {

  const token = localStorage.getItem("token")

  const res = await backendApi.post("/case_management/create_matter_type/",data, {
    headers: {
      Authorization: `Token ${token}`
    }
  })

  return res.data
}





export const getAllCases = async () => {

  const token = localStorage.getItem("token")

  const res = await backendApi.get("/case_management/get_all_cases", {
    headers: {
      Authorization: `Token ${token}`
    }
  })

  return res.data
}


// lib/api/cases.js

  export const getCaseDetails = async (case_id) => {
    const token = localStorage.getItem("token")

    const res = await backendApi.get(
      `/case_management/get_case_details/${case_id}/`,
      {
        headers: {
          Authorization: `Token ${token}`
        }
      }
    );
    console.log('res', res.data)

    return res.data
  }


  export const updateCase = async (case_id, data) => {
  const token = localStorage.getItem("token")

  const res = await backendApi.patch(
    `/case_management/update_case/${case_id}/`,
    data,
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  )

  return res.data
}



export const getFirmMembers = async () => {
  const token = localStorage.getItem("token")

  const res = await backendApi.get(
    "/case_management/get_firm_members/",
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  )

  return res.data.data
}

export const assignToCase = async (caseId, data) => {
  const token = localStorage.getItem("token")

  const res = await backendApi.post(
    `/case_management/assign_to_case/${caseId}/`,
    data, // ✅ PASS DIRECTLY
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  )

  return res.data
}


// export const assignToCase = async (caseId, userId) => {
//   const token = localStorage.getItem("token")

//   const res = await backendApi.post(
//     `/case_management/assign_to_case/${caseId}/`,
//     { target_user: userId },
//     {
//       headers: {
//         Authorization: `Token ${token}`
//       }
//     }
//   )

//   return res.data
// }
// export const getCaseDetails = async (case_id) => {
//   const token = localStorage.getItem("token")

//   const res = await backendApi.get(
//     `/case_management/get_case_details/${case_id}/`,
//     {
//       headers: {
//         Authorization: `Token ${token}`
//       }
//     },
//     crossOriginIsolated.log("resssssssssssssssssssss")
//   )

//   return res.data
//}
// export const createMatterType = async (data) => {
//   try {
//     const res = await fetch("/case_management/create_matter_type/", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//       },
//       body: JSON.stringify(data),
//     })

//     if (!res.ok) {
//       throw new Error("Failed to create matter type")
//     }

//     return await res.json()

//   } catch (error) {
//     console.error("Create matter type error:", error)
//     throw error
//   }
// }