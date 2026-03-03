import backendApi from "./backendApi";

export const getCsrfToken = async () => {
  // 1. Try cookie first
  const cookieToken = document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="))
    ?.split("=")[1];

  if (cookieToken) return cookieToken;

  // 2. Otherwise fetch it
  const res = await backendApi.get("/system_management/csrf/");
  return res.data?.csrfToken;
};
