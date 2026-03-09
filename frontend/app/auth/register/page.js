"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { register_Firm_Owner } from "../../../lib/api/users";



// export const register_Firm_Owner = async (data) => {
//   const response = await backendApi.post(
//     consolele.log('testing this file'),
//     "/system_management/register_firm_owner/",
//     data
//   );

//   return response.data;
// };


export default function RegisterFirmWithOwner() {
  
  
  const router = useRouter();

  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const data = await register_Firm_Owner(form);

      if (data.status === "success") {
        setSuccess(true);

        setTimeout(() => {
          router.push("/login");
        }, 1500);
      } else {
        setError(data.message || "Registration failed.");
      }
    } catch (err) {
      setError(
        err?.response?.data?.message ||
          "Registration failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 mt-20">
      <h1 className="text-2xl font-bold mb-6">Create Firm Owner Account</h1>

      {success && (
        <p className="text-green-600 mb-4">
          Account created successfully. Redirecting to login...
        </p>
      )}

      {error && <p className="text-red-600 mb-4">{error}</p>}

      <form onSubmit={handleSubmit} className="space-y-4">

        {/* Honeypot */}
        <input type="text" name="company" className="hidden" />

        <input
          name="first_name"
          placeholder="First name"
          required
          value={form.first_name}
          onChange={handleChange}
          className="w-full border rounded p-2"
        />

        <input
          name="last_name"
          placeholder="Last name"
          required
          value={form.last_name}
          onChange={handleChange}
          className="w-full border rounded p-2"
        />

        <input
          name="email"
          type="email"
          placeholder="Email"
          required
          value={form.email}
          onChange={handleChange}
          className="w-full border rounded p-2"
        />

        <input
          name="password"
          type="password"
          placeholder="Password"
          required
          value={form.password}
          onChange={handleChange}
          className="w-full border rounded p-2"
        />

        <button
          type="submit"
          disabled={loading || success}
          className="bg-black text-white px-4 py-2 rounded w-full"
        >
          {loading ? "Creating..." : "Create Account"}
        </button>
      </form>
    </div>
  );
}