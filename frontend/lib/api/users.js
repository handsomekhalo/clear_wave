import backendApi from "@/utils/backendApi";

export const register_Firm_Owner = async (payload) => {
  // payload should be a plain object:
  // {
  //   first_name, last_name, email, password, firm_name
  // }

  const response = await backendApi.post(
    "/system_management/register_firm_owner/",
    payload,
    {
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  return response.data;
};

// export const registerFirmOwner = async (data) => {
//   const response = await backendApi.post(
//     console.log('im on this file'),
//     "/system_management_api/register_firm_owner_api/",
//     data
//   );
//   return response.data;
// };