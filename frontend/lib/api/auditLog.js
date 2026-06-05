// frontend/lib/api/auditlog.js

import backendApi from "../backendApi";

/**
 * List audit logs for the current firm.
 *
 * @param {object} params
 * @returns paginated response
 */
export const getAuditLogs = async ({
  page = 1,
  page_size = 50,
  model_type = "",
  search = "",
} = {}) => {
  const token = localStorage.getItem("token");

  const res = await backendApi.get(
    "/system_management/get_audit_logs/",
    {
      params: {
        page,
        page_size,
        ...(model_type && { model_type }),
        ...(search && { search }),
      },
      headers: {
        Authorization: `Token ${token}`,
      },
    }
  );

  return res.data.data;
};

/**
 * Get details for a single audit log.
 *
 * @param {number} logId
 */
export const getAuditLogDetail = async (logId) => {
  const token = localStorage.getItem("token");

  const res = await backendApi.get(
    `/system_management/get_audit_log_detail/${logId}/`,
    {
      headers: {
        Authorization: `Token ${token}`,
      },
    }
  );

  return res.data.data;
};