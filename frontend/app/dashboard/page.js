"use client";

import { useAuth } from "../../AuthContext";

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div>
      <h1>Welcome, {user?.first_name || "User"}</h1>
      <p>Dashboard content here.</p>
    </div>
  );
}