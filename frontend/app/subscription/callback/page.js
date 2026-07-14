"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { verifySubscription } from "../../../lib/api/subscriptionApi";

export default function SubscriptionCallbackPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [state, setState] = useState("loading");
  const [plan, setPlan] = useState("");

  useEffect(() => {
    const reference = searchParams.get("reference") || searchParams.get("trxref");
    const success = searchParams.get("success");
    const error = searchParams.get("error");

    // Already processed by backend redirect
    if (success === "true") {
      setPlan(searchParams.get("plan") || "");
      setState("success");
      return;
    }

    if (error) {
      setState("error");
      return;
    }

    // Fresh from Paystack — verify now
    if (reference) {
      verifySubscription(reference)
        .then((data) => {
          if (data.status === "success") {
            setPlan(data.data?.plan || "");
            setState("success");
          } else {
            setState("error");
          }
        })
        .catch(() => setState("error"));
      return;
    }

    setState("error");
  }, []);

  const PLAN_LABELS = {
    solo: "Solo",
    small_firm: "Small Firm",
    growing_firm: "Growing Firm",
  };

  if (state === "loading") {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-gray-500 text-sm">Confirming your subscription...</p>
      </div>
    );
  }

  if (state === "success") {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen px-4">
        <div className="max-w-md w-full text-center">
          <div className="text-5xl mb-4">✓</div>
          <h1 className="text-2xl font-semibold text-gray-900">
            You're subscribed
          </h1>
          <p className="text-gray-500 mt-2">
            {PLAN_LABELS[plan] || "Your"} plan is now active.
          </p>
          <button
            onClick={() => router.push("/dashboard")}
            className="mt-6 px-6 py-2.5 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4">
      <div className="max-w-md w-full text-center">
        <div className="text-5xl mb-4">✕</div>
        <h1 className="text-2xl font-semibold text-gray-900">
          Something went wrong
        </h1>
        <p className="text-gray-500 mt-2">
          Your subscription could not be activated. No payment was taken.
        </p>
        <button
          onClick={() => router.push("/subscription/plans")}
          className="mt-6 px-6 py-2.5 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    </div>
  );
}

// "use client";

// import { useEffect, useState } from "react";
// import { useSearchParams, useRouter } from "next/navigation";

// export default function SubscriptionCallbackPage() {
//   const searchParams = useSearchParams();
//   const router = useRouter();
//   const [state, setState] = useState("loading"); // loading | success | error

//   const success = searchParams.get("success");
//   const plan = searchParams.get("plan");
//   const error = searchParams.get("error");

//   useEffect(() => {
//     if (success === "true") {
//       setState("success");
//     } else if (error) {
//       setState("error");
//     }
//   }, [success, error]);

//   const PLAN_LABELS = {
//     solo: "Solo",
//     small_firm: "Small Firm",
//     growing_firm: "Growing Firm",
//   };

//   if (state === "loading") {
//     return (
//       <div className="flex items-center justify-center min-h-screen">
//         <p className="text-gray-500 text-sm">Confirming your subscription...</p>
//       </div>
//     );
//   }

//   if (state === "success") {
//     return (
//       <div className="flex flex-col items-center justify-center min-h-screen px-4">
//         <div className="max-w-md w-full text-center">
//           <div className="text-5xl mb-4">✓</div>
//           <h1 className="text-2xl font-semibold text-gray-900">
//             You're subscribed
//           </h1>
//           <p className="text-gray-500 mt-2">
//             {PLAN_LABELS[plan] || "Your"} plan is now active.
//           </p>
//           <button
//             onClick={() => router.push("/dashboard")}
//             className="mt-6 px-6 py-2.5 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors"
//           >
//             Go to Dashboard
//           </button>
//         </div>
//       </div>
//     );
//   }

//   return (
//     <div className="flex flex-col items-center justify-center min-h-screen px-4">
//       <div className="max-w-md w-full text-center">
//         <div className="text-5xl mb-4">✕</div>
//         <h1 className="text-2xl font-semibold text-gray-900">
//           Something went wrong
//         </h1>
//         <p className="text-gray-500 mt-2">
//           Your subscription could not be activated. No payment was taken.
//         </p>
//         <button
//         //   onClick={() => router.push("/subscription/plans")}
//           onClick={() => router.push("/subscription/plans")}

//           className="mt-6 px-6 py-2.5 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors"
//         >
//           Try Again
//         </button>
//       </div>
//     </div>
//   );
// }