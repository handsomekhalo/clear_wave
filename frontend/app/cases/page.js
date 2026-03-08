"use client";

import { useState } from "react";
import TopBar from "@/components/layout/TopBar";
import CasesTable from "@/components/cases/CasesTable";
import NewCaseDialog from "@/components/cases/NewCaseDialog";
import Sidebar from '../../components/layout/SideBar';

export default function CasesPage() {
  const [cases, setCases] = useState([
    {
      id: 1,
      title: "Smith vs Johnson",
      client_name: "John Smith",
      status: "active",
      assigned_lawyer: "Titus Monaheng",
      deadline: "2026-04-15",
      case_number: "2026-001",
    },
    {
      id: 2,
      title: "ABC Corp Contract Review",
      client_name: "ABC Corp",
      status: "pending",
      assigned_lawyer: "Jane Doe",
      deadline: "2026-05-10",
      case_number: "2026-002",
    },
  ]);

  const [open, setOpen] = useState(false);
  const [editingCase, setEditingCase] = useState(null);
  const [collapsed, setCollapsed] = useState(false);

  const handleSave = (formData, id) => {
    if (id) {
      // Edit
      setCases((prev) =>
        prev.map((c) => (c.id === id ? { ...c, ...formData } : c))
      );
    } else {
      // Create
      const newCase = {
        id: Date.now(),
        ...formData,
      };
      setCases((prev) => [...prev, newCase]);
    }

    setOpen(false);
    setEditingCase(null);
  };

  const handleEdit = (caseItem) => {
    setEditingCase(caseItem);
    setOpen(true);
  };

  const handleDelete = (caseItem) => {
    setCases((prev) => prev.filter((c) => c.id !== caseItem.id));
  };

return (
 <div className="flex">

  <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />

  <main
    className={`flex-1 transition-all duration-300 ${
      collapsed ? "ml-[68px]" : "ml-[240px]"
    }`}
  >
    <TopBar title="Cases" onNewCase={() => setOpen(true)} />

    <div className="p-6 overflow-x-auto">
      <CasesTable
        cases={cases}
        isLoading={false}
        onEdit={() => {}}
        onDelete={() => {}}
      />
    </div>

    <NewCaseDialog
      open={open}
      onOpenChange={setOpen}
      onSave={handleSave}
      editingCase={editingCase}
    />

  </main>

</div>
);
}