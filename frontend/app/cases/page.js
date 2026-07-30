"use client";

import { useState, useEffect, useCallback } from "react";
import SideBar from "@/components/layout/SideBar";
import TopBar from "@/components/layout/TopBar";
import CasesTable from "@/components/cases/CasesTable";
import NewCaseDialog from "@/components/cases/NewCaseDialog";
import { ViewCaseModal } from "../../components/cases/ViewCaseModal";
import { getAllCases } from "../../lib/api/cases";
import { createCase } from "../../lib/api/cases";
import { updateCase } from "../../lib/api/cases";

export default function CasesPage() {
  const [cases, setCases] = useState([]);
  const [open, setOpen] = useState(false);
  const [editingCase, setEditingCase] = useState(null);
  const [collapsed, setCollapsed] = useState(false);
  const [viewCaseId, setViewCaseId] = useState(null);
  const [viewOpen, setViewOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // ✅ FIX 1: Fetch real cases from the API
  const fetchCases = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getAllCases();
      setCases(Array.isArray(res) ? res : res.data ?? []);
    } catch (err) {
      console.error("Failed to load cases", err);
      setError("Failed to load cases. Please refresh.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCases();
  }, [fetchCases]);

  const handleView = (c) => {
    setViewCaseId(c.id);
    setViewOpen(true);
  };

  const handleEdit = (caseItem) => {
    setEditingCase(caseItem);
    setOpen(true);
  };

  const handleDelete = async (caseItem) => {
    if (!confirm(`Delete case "${caseItem.title}"?`)) return;
    try {
      await deleteCase(caseItem.id);
      await fetchCases(); // ✅ Refresh after delete
    } catch (err) {
      console.error("Failed to delete case", err);
      alert("Failed to delete case. Please try again.");
    }
  };

  // ✅ FIX 2: handleSave calls real API then refreshes the list
  const handleSave = async (formData, id) => {
    try {
      if (id) {
        await updateCase(id, {
          title: formData.title,
          description: formData.description,
          status: formData.status,
          deadline: formData.deadline || null,
          matter_type: formData.matter_type ? Number(formData.matter_type) : null,
        });
      } else {
        await createCase({
          title: formData.title,
          client_id: formData.client_id ? Number(formData.client_id) : null,
          description: formData.description,
          status: formData.status,
          deadline: formData.deadline || null,
          matter_type: formData.matter_type ? Number(formData.matter_type) : null,
        });
      }
      // ✅ FIX 3: Refresh so new/updated case appears in the list immediately
      await fetchCases();
      setOpen(false);
      setEditingCase(null);
    } catch (err) {
      console.error("Failed to save case", err);
      throw err; // Let NewCaseDialog surface the error
    }
  };

  return (
    <div className="flex">
      <SideBar collapsed={collapsed} setCollapsed={setCollapsed} />
      <main
        className={`flex-1 transition-all duration-300 ${
          collapsed ? "ml-[68px]" : "ml-[240px]"
        }`}
      >
        <TopBar title="Cases" onNewCase={() => setOpen(true)} />

        <div className="p-6 overflow-x-auto">
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="flex flex-col items-center gap-3 text-gray-400">
                <svg
                  className="animate-spin h-8 w-8"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
                <span className="text-sm">Loading cases...</span>
              </div>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-20 gap-3 text-red-500">
              <p>{error}</p>
              <button onClick={fetchCases} className="text-sm underline text-blue-600">
                Try again
              </button>
            </div>
          ) : (
            <CasesTable
              cases={cases}
              isLoading={false}
              onEdit={handleEdit}
              onDelete={handleDelete}
              onView={handleView}
            />
          )}
        </div>

        <NewCaseDialog
          open={open}
          onOpenChange={(val) => {
            setOpen(val);
            if (!val) setEditingCase(null);
          }}
          onSave={handleSave}
          editingCase={editingCase}
        />

        <ViewCaseModal
          open={viewOpen}
          onOpenChange={setViewOpen}
          caseId={viewCaseId}
          onUpdate={fetchCases}
        />
      </main>
    </div>
  );
}


// "use client";

// import { useState } from "react";
// import TopBar from "@/components/layout/TopBar";
// import CasesTable from "@/components/cases/CasesTable";
// import NewCaseDialog from "@/components/cases/NewCaseDialog";
// import Sidebar from '../../components/layout/SideBar';
// import { ViewCaseModal } from "../../components/cases/ViewCaseModal";


// export default function CasesPage() {
//   const [cases, setCases] = useState([
//     {
//       id: 1,
//       title: "Smith vs Johnson",
//       client_name: "John Smith",
//       status: "active",
//       assigned_lawyer: "Titus Monaheng",
//       deadline: "2026-04-15",
//       case_number: "2026-001",
//     },
//     {
//       id: 2,
//       title: "ABC Corp Contract Review",
//       client_name: "ABC Corp",
//       status: "pending",
//       assigned_lawyer: "Jane Doe",
//       deadline: "2026-05-10",
//       case_number: "2026-002",
//     },
//   ]);

//   const [open, setOpen] = useState(false);
//   const [editingCase, setEditingCase] = useState(null);
//   const [collapsed, setCollapsed] = useState(false);

//   const [viewCaseId, setViewCaseId] = useState(null)
//   const [viewOpen, setViewOpen] = useState(false)

//     const handleView = (c) => {
//       setViewCaseId(c.id)
//       setViewOpen(true)
//     }
  
    

//   const handleSave = (formData, id) => {
//     if (id) {
//       // Edit
//       setCases((prev) =>
//         prev.map((c) => (c.id === id ? { ...c, ...formData } : c))
//       );
//     } else {
//       // Create
//       const newCase = {
//         id: Date.now(),
//         ...formData,
//       };
//       setCases((prev) => [...prev, newCase]);
//     }

//     setOpen(false);
//     setEditingCase(null);
//   };

//   const handleEdit = (caseItem) => {
//     setEditingCase(caseItem);
//     setOpen(true);
//   };

//   const handleDelete = (caseItem) => {
//     setCases((prev) => prev.filter((c) => c.id !== caseItem.id));
//   };

// return (
//  <div className="flex">

//   <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />

//   <main
//     className={`flex-1 transition-all duration-300 ${
//       collapsed ? "ml-[68px]" : "ml-[240px]"
//     }`}
//   >
//     <TopBar title="Cases" onNewCase={() => setOpen(true)} />

//     <div className="p-6 overflow-x-auto">
//       <CasesTable
//   cases={cases}
//   isLoading={false}
//   onEdit={handleEdit}
//   onDelete={handleDelete}
//   onView={handleView}
  
// />

//     </div>

//     <NewCaseDialog
//       open={open}
//       onOpenChange={setOpen}
//       onSave={handleSave}
//       editingCase={editingCase}
//     />

//     <ViewCaseModal
//   open={viewOpen}
//   onOpenChange={setViewOpen}
//   caseId={viewCaseId}
// />



//   </main>

// </div>
// );
// }