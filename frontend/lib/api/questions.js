import backendApi from "../backendApi"
import {useAuth} from "../../AuthContext"


const getToken = () => localStorage.getItem("token");

const authHeaders = () => ({
  "Content-Type": "application/json",
  Authorization: `Token ${getToken()}`,
});

// QUESTION BANK
// ---------------------------------------------------------------------------

export const listQuestions = async () => {
  const res = await backendApi.get(
    "/forms_engine_management/list_questions/",
    { headers: authHeaders() }
  );
  return res.data;
};

export const getQuestion = async (questionId) => {
  const res = await backendApi.get(
    `/forms_engine_management/get_question/${questionId}/`,
    { headers: authHeaders() }
  );
  return res.data;
};

export const createQuestion = async (data) => {
  const res = await backendApi.post(
    "/forms_engine_management/create_question/",
    data,
    { headers: authHeaders() }
  );
  return res.data;
};

export const updateQuestion = async (questionId, data) => {
  const res = await backendApi.patch(
    `/forms_engine_management/update_question/${questionId}/`,
    data,
    { headers: authHeaders() }
  );
  return res.data;
};

// ---------------------------------------------------------------------------
// QUESTION OPTIONS
// ---------------------------------------------------------------------------

export const listQuestionOptions = async (questionId) => {
  const res = await backendApi.get(
    `/forms_engine_management/list_question_options/${questionId}/`,
    { headers: authHeaders() }
  );
  return res.data;
};

export const addQuestionOption = async (questionId, data) => {
  const res = await backendApi.post(
    `/forms_engine_management/add_question_option/${questionId}/`,
    data,
    { headers: authHeaders() }
  );
  return res.data;
};

export const updateQuestionOption = async (questionId, optionId, data) => {
  const res = await backendApi.patch(
    `/forms_engine_management/update_question_option/${questionId}/${optionId}/`,
    data,
    { headers: authHeaders() }
  );
  return res.data;
};

export const deleteQuestionOption = async (questionId, optionId) => {
  const res = await backendApi.delete(
    `/forms_engine_management/delete_question_option/${questionId}/${optionId}/`,
    { headers: authHeaders() }
  );
  return res.data;
};

// ---------------------------------------------------------------------------
// SECTION QUESTION ASSIGNMENT
// ---------------------------------------------------------------------------

export const listSectionQuestions = async (templateId, sectionId) => {
  const res = await backendApi.get(
    `/forms_engine_management/list_section_questions/${templateId}/${sectionId}/`,
    { headers: authHeaders() }
  );
  return res.data;
};

export const assignQuestionToSection = async (templateId, sectionId, data) => {
  const res = await backendApi.post(
    `/forms_engine_management/assign_question_to_section/${templateId}/${sectionId}/`,
    data,
    { headers: authHeaders() }
  );
  return res.data;
};

export const updateSectionQuestion = async (templateId, sectionId, sqId, data) => {
  const res = await backendApi.patch(
    `/forms_engine_management/update_section_question/${templateId}/${sectionId}/${sqId}/`,
    data,
    { headers: authHeaders() }
  );
  return res.data;
};

export const removeQuestionFromSection = async (templateId, sectionId, sqId) => {
  const res = await backendApi.delete(
    `/forms_engine_management/remove_question_from_section/${templateId}/${sectionId}/${sqId}/`,
    { headers: authHeaders() }
  );
  return res.data;
};

// ---------------------------------------------------------------------------
// CASE FORM ASSIGNMENT
// ---------------------------------------------------------------------------

export const listCaseFormAssignments = async (caseId) => {
  const res = await backendApi.get(
    `/forms_engine_management/list_case_form_assignments/${caseId}/`,
    { headers: authHeaders() }
  );
  return res.data;
};

export const getCaseFormAssignment = async (caseId, assignmentId) => {
  const res = await backendApi.get(
    `/forms_engine_management/get_case_form_assignment/${caseId}/${assignmentId}/`,
    { headers: authHeaders() }
  );
  return res.data;
};

export const assignFormToCase = async (caseId, data) => {
  const res = await backendApi.post(
    `/forms_engine_management/assign_form_to_case/${caseId}/`,
    data,
    { headers: authHeaders() }
  );
  return res.data;
};

export const reviewCaseFormAssignment = async (caseId, assignmentId, data) => {
  const res = await backendApi.post(
    `/forms_engine_management/review_case_form_assignment/${caseId}/${assignmentId}/`,
    data,
    { headers: authHeaders() }
  );
  return res.data;
};
