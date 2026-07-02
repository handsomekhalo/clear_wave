'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import FirmOnboardingStepOne from '../../components/firm_onboarding_components/onboarding_step_1';
import FirmOnboardingStepTwo from '../../components/firm_onboarding_components/onboarding_step_2';

function FirmOnboardingContent() {
  const searchParams = useSearchParams();
  const step = searchParams.get('step') || '1';

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-6">
      <div className="w-full max-w-md">

        <div className="mb-6 flex items-center justify-center gap-2 text-sm text-gray-500">
          <span className={step === '1' ? 'font-semibold text-indigo-600' : ''}>
            Step 1
          </span>

          <span>→</span>

          <span className={step === '2' ? 'font-semibold text-indigo-600' : ''}>
            Step 2
          </span>
        </div>

        {step === '1' && <FirmOnboardingStepOne />}
        {step === '2' && <FirmOnboardingStepTwo />}

      </div>
    </div>
  );
}

export default function FirmOnboardingPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
      <FirmOnboardingContent />
    </Suspense>
  );
}


// 'use client';

// import { useSearchParams } from 'next/navigation';
// import FirmOnboardingStepOne from '../../components/firm_onboarding_components/onboarding_step_1';
// import FirmOnboardingStepTwo from '../../components/firm_onboarding_components/onboarding_step_2';

// export default function FirmOnboardingPage() {
//   const searchParams = useSearchParams();
//   const step = searchParams.get('step') || '1';

//   return (
//     <div className="min-h-screen flex items-center justify-center bg-gray-50 px-6">
//       <div className="w-full max-w-md">

//         {/* Progress indicator */}
//         <div className="mb-6 flex items-center justify-center gap-2 text-sm text-gray-500">
//           <span className={step === '1' ? 'font-semibold text-indigo-600' : ''}>
//             Step 1
//           </span>

//           <span>→</span>

//           <span className={step === '2' ? 'font-semibold text-indigo-600' : ''}>
//             Step 2
//           </span>
//         </div>

//         {/* Step Content */}
//         {step === '1' && <FirmOnboardingStepOne />}
//         {step === '2' && <FirmOnboardingStepTwo />}

//       </div>
//     </div>
//   );
// }