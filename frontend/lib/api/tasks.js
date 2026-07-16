import backendApi from "../backendApi";

export const listCaseTasks = async (caseId) => {
  const token = localStorage.getItem("authToken");
  const res = await backendApi.get(`/case_management/list_case_tasks/${caseId}/`, {
    headers: { Authorization: `Token ${token}` },
  });
  return res.data;
};

export const createTask = async (caseId, data) => {
  const token = localStorage.getItem("authToken");
  const res = await backendApi.post(`/case_management/create_task/${caseId}/`, data, {
    headers: { Authorization: `Token ${token}` },
  });
  return res.data;
};

export const updateTask = async (caseId, taskId, data) => {
  const token = localStorage.getItem("authToken");
  const res = await backendApi.patch(
    `/case_management/update_task/${caseId}/${taskId}/`,
    data,
    { headers: { Authorization: `Token ${token}` } }
  );
  return res.data;
};

export const deleteTask = async (caseId, taskId) => {
  const token = localStorage.getItem("authToken");
  const res = await backendApi.delete(
    `/case_management/delete_task/${caseId}/${taskId}/`,
    { headers: { Authorization: `Token ${token}` } }
  );
  return res.data;
};