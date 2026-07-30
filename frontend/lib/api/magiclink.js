import backendApi from "../backendApi"

export const getClientMagicLinkStatus = async (clientId) => {
  const res = await backendApi.get(`/client_management/get_client_magic_link_status/${clientId}/`)
  return res.data?.data ?? res.data
}

export const sendClientMagicLink = async (clientId) => {
  const res = await backendApi.post(`/client_management/send_client_magic_link/${clientId}/`)
  return res.data?.data ?? res.data
}