
import backendApi from "../backendApi"
import { useAuth } from "../../AuthContext";

// ---------------------------------------------------------------------------
// FORM SUBMISSIONS
// ---------------------------------------------------------------------------

export const startFormSubmission = async (assignmentId) => {
  const token = localStorage.getItem("token");

  const res = await backendApi.post(
    `/forms_engine_management/start_form_submission/${assignmentId}/`,
    {},
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  );

  return res.data;
};

export const getFormSubmission = async (assignmentId) => {
  const token = localStorage.getItem("token");

  const res = await backendApi.get(
    `/forms_engine_management/get_form_submission/${assignmentId}/`,
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  );

  return res.data;
};

// ---------------------------------------------------------------------------
// FORM RESPONSES
// ---------------------------------------------------------------------------

export const saveFormResponse = async (submissionId, data) => {
  const token = localStorage.getItem("token");

  const res = await backendApi.post(
    `/forms_engine_management/save_form_response/${submissionId}/`,
    data,
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  );

  return res.data;
};

export const listFormResponses = async (submissionId) => {
  const token = localStorage.getItem("token");

  const res = await backendApi.get(
    `/forms_engine_management/list_form_responses/${submissionId}/`,
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  );

  return res.data;
};

export const submitForm = async (submissionId) => {
  const token = localStorage.getItem("token");

  const res = await backendApi.post(
    `/forms_engine_management/submit_form/${submissionId}/`,
    {},
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  );

  return res.data;
};



// import backendApi from "@/utils/backendApi";
// import {useAuth} from "../../AuthContext"


// const getToken = () => localStorage.getItem("token");

// const authHeaders = () => ({
//   "Content-Type": "application/json",
//   Authorization: `Token ${getToken()}`,
// });




// export const startFormSubmission = async (assignmentId) => {
//   const res = await backendApi.post(
//     `/forms_engine_management/start_form_submission/${assignmentId}/`,
//     {},
//     { headers: authHeaders() }
//   );
//   return res.data;
// };

// export const getFormSubmission = async (assignmentId) => {
//   const res = await backendApi.get(
//     `/forms_engine_management/get_form_submission/${assignmentId}/`,
//     { headers: authHeaders() }
//   );
//   return res.data;
// };

// // ---------------------------------------------------------------------------
// // FORM RESPONSES
// // ---------------------------------------------------------------------------

// export const saveFormResponse = async (submissionId, data) => {
//   const res = await backendApi.post(
//     `/forms_engine_management/save_form_response/${submissionId}/`,
//     data,
//     { headers: authHeaders() }
//   );
//   return res.data;
// };

// export const listFormResponses = async (submissionId) => {
//   const res = await backendApi.get(
//     `/forms_engine_management/list_form_responses/${submissionId}/`,
//     { headers: authHeaders() }
//   );
//   return res.data;
// };

// export const submitForm = async (submissionId) => {
//   const res = await backendApi.post(
//     `/forms_engine_management/submit_form/${submissionId}/`,
//     {},
//     { headers: authHeaders() }
//   );
//   return res.data;
// };
