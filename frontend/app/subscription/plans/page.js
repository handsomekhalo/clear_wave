"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { initializeSubscription } from "../../../lib/api/subscriptionApi";

const PLANS = [
  {
    id: "solo",
    name: "Solo",
    price: "R350",
    description: "For solo practitioners and independent legal consultants.",
    features: [
      "1 user",
      "Unlimited cases",
      "Document management",
      "Client portal",
      "Audit logs",
      "Form templates",
    ],
  },
  {
    id: "small_firm",
    name: "Small Firm",
    price: "R750",
    description: "For small firms of 2–3 lawyers.",
    features: [
      "3 users",
      "Unlimited cases",
      "Everything in Solo",
      "Team access",
      "Role-based permissions",
    ],
  },
  {
    id: "growing_firm",
    name: "Growing Firm",
    price: "R1,500",
    description: "For growing practices of up to 10 users.",
    features: [
      "10 users",
      "Unlimited cases",
      "Everything in Small Firm",
      "Advanced audit trails",
      "Priority support",
    ],
  },
];

export default function PlansPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(null);
  const [error, setError] = useState("");
  const [ready, setReady] = useState(false);



const handleSubscribe = async (planId) => {
    const token = localStorage.getItem("authToken");
    if (!token) {
      router.push("/login");
      return;
    }

  setLoading(planId);
  setError("");

    try {
      const data = await initializeSubscription(planId);
      window.location.href = data.data.authorization_url;
    } catch (err) {
      setError(
        err?.response?.data?.error || "Something went wrong. Please try again."
      );
      setLoading(null);
    }
  };;

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      <div className="mb-10">
        <h1 className="text-2xl font-semibold text-gray-900">Choose a Plan</h1>
        <p className="text-gray-500 mt-1">Start free. Upgrade when you're ready.</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {PLANS.map((plan) => (
          <div
            key={plan.id}
            className="border border-gray-200 rounded-xl p-6 flex flex-col justify-between hover:border-gray-400 transition-colors"
          >
            <div>
              <h2 className="text-lg font-semibold text-gray-900">{plan.name}</h2>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {plan.price}
                <span className="text-base font-normal text-gray-500">/month</span>
              </p>
              <p className="text-sm text-gray-500 mt-2">{plan.description}</p>

              <ul className="mt-4 space-y-2">
                {plan.features.map((feature) => (
                  <li
                    key={feature}
                    className="flex items-center gap-2 text-sm text-gray-700"
                  >
                    <span className="text-green-500">✓</span>
                    {feature}
                  </li>
                ))}
              </ul>
            </div>

            <button
              onClick={() => handleSubscribe(plan.id)}
              disabled={loading === plan.id}
              className="mt-6 w-full py-2.5 px-4 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading === plan.id ? "Redirecting..." : "Subscribe"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}