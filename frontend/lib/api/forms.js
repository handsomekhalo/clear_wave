' use client';
import backendApi from "../backendApi"
import { useAuth } from "../../AuthContext";

// ---------------------------------------------------------------------------
// FORM TEMPLATES
// ---------------------------------------------------------------------------

export const listFormTemplates = async () => {
  const token = localStorage.getItem("token");

  const res = await backendApi.get(
    "/forms_engine_management/list_form_templates/",
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  );

  console.log("Form templates response:", res.data); // Debug log

  return res.data;
};

export const getFormTemplate = async (templateId) => {
  const token = localStorage.getItem("token");

  const res = await backendApi.get(
    `/forms_engine_management/get_form_template/${templateId}/`,
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  );

  return res.data;
};

export const createFormTemplate = async (data) => {
  const token = localStorage.getItem("token");

  const res = await backendApi.post(
    "/forms_engine_management/create_form_template/",
    data,
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  );

  return res.data;
};

export const updateFormTemplate = async (templateId, data) => {
  const token = localStorage.getItem("token");

  const res = await backendApi.patch(
    `/forms_engine_management/update_form_template/${templateId}/`,
    data,
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  );

  return res.data;
};

// ---------------------------------------------------------------------------
// FORM SECTIONS
// ---------------------------------------------------------------------------

export const listFormSections = async (templateId) => {
  const token = localStorage.getItem("token");

  const res = await backendApi.get(
    `/forms_engine_management/list_form_sections/${templateId}/`,
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  );

  return res.data;
};

export const createFormSection = async (templateId, data) => {
  const token = localStorage.getItem("token");

  const res = await backendApi.post(
    `/forms_engine_management/create_form_section/${templateId}/`,
    data,
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  );

  return res.data;
};

export const updateFormSection = async (
  templateId,
  sectionId,
  data
) => {
  const token = localStorage.getItem("token");

  const res = await backendApi.patch(
    `/forms_engine_management/update_form_section/${templateId}/${sectionId}/`,
    data,
    {
      headers: {
        Authorization: `Token ${token}`
      }
    }
  );

  return res.data;
};