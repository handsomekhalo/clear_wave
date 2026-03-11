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


