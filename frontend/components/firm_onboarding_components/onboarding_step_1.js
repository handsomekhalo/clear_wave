'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import backendApi from '@/lib/backendApi';

export default function FirmOnboardingStepOne() {

  const router = useRouter();
  const [firmName, setFirmName] = useState('');

  const submit = async () => {

    try {

      await backendApi.post(
        '/system_management/firm_onboarding_step_1/',
        { name: firmName }
      );

      router.push('/firm_onboarding?step=2');

    } catch (err) {

      console.error(
        'Step 1 onboarding error:',
        err.response?.data || err.message
      );

    }

  };

  return (
    <div className="max-w-md mx-auto mt-20 space-y-4">

      <h1 className="text-2xl font-bold">
        Create Your Firm
      </h1>

      <input
        placeholder="Firm Name"
        className="w-full border rounded p-2"
        value={firmName}
        onChange={(e) => setFirmName(e.target.value)}
      />

      <button
        onClick={submit}
        className="w-full bg-indigo-600 text-white py-2 rounded"
      >
        Continue
      </button>

    </div>
  );
}