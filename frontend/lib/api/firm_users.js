import backendApi from "../backendApi";
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

  return res.data
}



export const getFirmUserDetails = async (user_id) => {
  const token = localStorage.getItem("token")

  const res = await backendApi.get(`/system_management/firm_user_retrieve/${user_id}/`, {
    headers: {
      Authorization: `Token ${token}`
    }
  })

  return res.data
}

export const updateFirmUser = async (user_id, payload) => {

  const token = localStorage.getItem("token")

  const res = await backendApi.patch(
    `/system_management/firm_user_update/${user_id}/`,
    payload,
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  )

  return res.data
}



export const toggleFirmUserStatus = async (user_id) => {

  const token = localStorage.getItem("token")

  const res = await backendApi.patch(
    `/system_management/firm_user_toggle_status/${user_id}/`,
    {},
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  )

  return res.data
}