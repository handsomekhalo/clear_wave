import backendApi from "../backendApi";


export const initializeSubscription = async (plan) => {
  const res = await backendApi.post(
    "/system_management/subscription_initialize/",
    { plan }
  );
  return res.data;
}


export const verifySubscription = async (reference) => {
  const res = await backendApi.get(
    `/system_management/subscription_callback/?reference=${reference}`
  );
  return res.data;
};

export const getSubscriptionStatus = async () => {
  const token = localStorage.getItem("authToken");
  const res = await backendApi.get("/system_management/get_subscription_status/", {
    headers: { Authorization: `Token ${token}` },
  });
  return res.data;
};