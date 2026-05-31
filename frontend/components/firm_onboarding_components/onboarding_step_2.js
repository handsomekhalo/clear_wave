'use client';

import { useRouter } from 'next/navigation';
import backendApi from "../../lib/backendApi"
export default function FirmOnboardingStepTwo() {

  const router = useRouter();

  const submit = async () => {

    try {

      await backendApi.post(
        '/system_management/firm_onboarding_step_2/'
      );

      router.push('/dashboard');

    } catch (err) {

      console.error(
        'Step 2 onboarding error:',
        err.response?.data || err.message
      );

    }

  };

  return (
    <div className="max-w-md mx-auto mt-20 space-y-4">

      <h1 className="text-2xl font-bold">
        Setup Complete
      </h1>

      <p className="text-gray-600">
        Your firm is ready. You can now start creating cases and inviting users.
      </p>

      <button
        onClick={submit}
        className="w-full bg-indigo-600 text-white py-2 rounded"
      >
        Finish Onboarding
      </button>

    </div>
  );
}