"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getSubscriptionStatus } from "../../lib/api/subscriptionApi";

export default function SubscriptionBanner() {
  const router = useRouter();
  const [status, setStatus] = useState(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    getSubscriptionStatus()
      .then(res => setStatus(res?.data ?? res))
      .catch(err => console.error("Failed to load subscription status", err));
  }, []);

  // Don't show if active, suspended, or dismissed
  if (!status || status.subscription_status === "active" || dismissed) {
    return null;
  }

  const isSuspended = status.subscription_status === "suspended";

  return (
    <div className={`w-full px-4 py-3 flex items-center justify-between text-sm ${
      isSuspended
        ? "bg-red-50 border-b border-red-200 text-red-800"
        : "bg-amber-50 border-b border-amber-200 text-amber-800"
    }`}>
      <div className="flex items-center gap-2">
        <span className="text-base">{isSuspended ? "⚠️" : "ℹ️"}</span>
        {isSuspended ? (
          <span>
            Your subscription has been suspended due to a failed payment.
            Please update your billing to restore access.
          </span>
        ) : (
          <span>
            You're on the <strong>Free Tier</strong> —
            limited to {status.max_active_cases} active cases and {status.max_users} user.
            Upgrade to unlock unlimited cases, more users, and full platform access.
          </span>
        )}
      </div>
      <div className="flex items-center gap-3 shrink-0 ml-4">
        <button
          onClick={() => router.push("/subscription/plans")}
          className={`px-3 py-1.5 rounded text-xs font-medium ${
            isSuspended
              ? "bg-red-600 text-white hover:bg-red-700"
              : "bg-amber-600 text-white hover:bg-amber-700"
          }`}
        >
          {isSuspended ? "Fix Billing" : "Upgrade Now"}
        </button>
        {!isSuspended && (
          <button
            onClick={() => setDismissed(true)}
            className="text-amber-600 hover:text-amber-800 text-xs underline"
          >
            Dismiss
          </button>
        )}
      </div>
    </div>
  );
}