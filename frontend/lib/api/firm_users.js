import backendApi from "@/utils/backendApi";
import {useAuth} from "../../AuthContext"


export async function createFirmUser(data) {
  const token = localStorage.getItem("token");

  const res = await backendApi.post(
    "/system_management/create_firm_user/",
    data,
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  );

  return res.data;
}

// export async function createFirmUser(data) {
//   const res = await backendApi.post(
//     "/system_management/create_firm_user/",
//     data
//   );

//   return res.data;
// }




export const getFirmUsers = async () => {
  const token = localStorage.getItem("token")

  const res = await backendApi.get("/system_management/get_firm_user_list/", {
    headers: {
      Authorization: `Token ${token}`
    }
  })

  return res.data;
}



export const getAllRoles = async () => {

  const token = localStorage.getItem("token")

  const res = await backendApi.get("/system_management/get_all_roles/", {
    headers: {
      Authorization: `Token ${token}`
    }
  })
  console.log('weeeeeeeeeeeeeeeeeeeeeeeeeeeeedpfdks[')

  return res.data
}



export const getFirmUserDetails = async (user_id) => {
  const token = localStorage.getItem("token")
  console.log("USER ID inside this is :", user_id)

  const res = await backendApi.get(`/system_management/firm_user_retrieve/${user_id}/`, {
    headers: {
      Authorization: `Token ${token}`
    }
  })

  return res.data
}
// export const getFirmUsers = async () => {
//   const res = await backendApi.get(
//     '/system_management/get_firm_user_list/',
    
//   );
//   return res.data;
// };


// export const getFirmUsers = async () => {
  
//   // const { authToken, isAuthenticated } = useAuth();

//   const res = await backendApi.get(
//     '/system_management/get_firm_user_list/',
//       {headers: {
//               Authorization: `Token ${authToken}`,
//             },}
//   );
//   return res.data;
// };


//  const res = await backendApi.get(
//           "/media_streaming_management/my_tracks/",
//           {
//             headers: {
//               Authorization: `Token ${authToken}`,
//             },
//           }
//         );