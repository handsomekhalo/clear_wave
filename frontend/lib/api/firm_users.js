import backendApi from "@/utils/backendApi";


export async function createFirmUser(data) {
  const res = await backendApi.post(
    "/system_management/create_firm_user/",
    data
  );

  return res.data;
}

export async function getFirmUsers() {
  const res = await backendApi.get(
    "/system_management/get_firm_users/"
  );

    return res.data;
}