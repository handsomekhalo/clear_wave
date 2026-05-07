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



// ── NEW: Get all firm members (lawyers, assistants, etc.) ─────────────────────
// Uses the same endpoint already working in ViewCaseModal / NewCaseDialog
export const getAllUsers = async () => {
  const token = localStorage.getItem("authToken");
  const res = await backendApi.get("/case_management/get_firm_members/", {
    headers: { Authorization: `Token ${token}` },
  });
  // API returns { status: "success", data: [ { id, name, role }, ... ] }
  return res.data?.data ?? res.data ?? [];
};
 
// ── NEW: Invite / add a new firm member ───────────────────────────────────────
// Uses register_firm_owner pattern but targeted at adding a team member.
// NOTE: If your backend exposes a dedicated invite endpoint in future,
// replace the URL below. For now we call register_firm_owner and pass the role.
export const inviteUser = async (payload) => {
  const token = localStorage.getItem("authToken");
  // Derive a username from email (before the @)
  const username = payload.email.split("@")[0].replace(/[^a-zA-Z0-9]/g, "");
  // Generate a temporary password
  const tempPassword = "TempPass123!";

  const response = await api.post(
    "/system_management/register_firm_owner/",
    {
      username,
      first_name: payload.first_name,
      last_name: payload.last_name,
      email: payload.email,
      role: payload.role,
      phone: payload.phone || "",
      password: tempPassword,
    },
    {
      headers: { Authorization: `Token ${token}` },
    }
  );
  return response.data;
};