'use client';

// import backendApi from '@/utils/backendApi';
import { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import backendApi from  '../utils/backendApi';
// frontend\src\utils\backendApi.js

import { useRouter } from 'next/navigation';  // Correct import for App Router

export default function LoginPage() {
  const { login: authLogin } = useAuth();
  const [csrfToken, setCsrfToken] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();  // This will now work with App Router

  // Fetch CSRF Token
  useEffect(() => {
    backendApi
      .get('/system_management/csrf/', { withCredentials: true })
      .then((res) => {
        if (res.data && res.data.csrfToken) {
          setCsrfToken(res.data.csrfToken);
        }
      })
      .catch((err) => {
        console.error('Failed to fetch CSRF:', err);
      });
  }, []);


const handleSubmit = async (e) => {
  e.preventDefault();
  setErrors('');
  setIsSubmitting(true);

  const csrfFromCookies = document.cookie
    .split('; ')
    .find((row) => row.startsWith('csrftoken='))?.split('=')[1];

  const tokenToUse = csrfToken || csrfFromCookies;

  if (!tokenToUse) {
    setErrors('CSRF token missing. Please refresh and try again.');
    setIsSubmitting(false);
    return;
  }

  try {
    console.log('Sending login request...');
    const response = await backendApi.post(
      '/system_management_api/login_api/',
      { email, password },
      {
        headers: {
          'X-CSRFToken': tokenToUse,
          'Content-Type': 'application/json',
        },
        withCredentials: true,
      }
    );

    console.log('Login response:', response.data);

  if (response.data.token) {
  console.log('Login successful!');
  const token = response.data.token;
  const user = response.data.user;
  const firm = response.data.firm;

  // Store auth data
  authLogin(token, tokenToUse);
  localStorage.setItem('authToken', token);
  localStorage.setItem('csrfToken', tokenToUse);
  localStorage.setItem('user', JSON.stringify(user));

  // 🔐 Onboarding logic for firm
  if (user.role === 'firm_owner') {  // or user.role.includes('firm')
    console.log('User is a firm owner. Checking onboarding status...');
    if (!firm?.is_onboarded) {
      router.replace(`/firm_onboarding?step=${firm?.onboarding_step || 1}`);
      return;
    }
    router.replace('./dashboard');
    return;
  }

  // fallback
  router.replace('./dashboard');
} else {
  console.log('Login failed: no token returned');
  setErrors(response.data.message || 'Login failed. Try again.');
}
  } catch (err) {
    console.error('Login error:', err);
    if (err.response) {
      setErrors(err.response.data?.message || 'An error occurred during login.');
    } else {
      setErrors('Network error. Please check your connection.');
    }
  } finally {
    setIsSubmitting(false);
  }
};
  // const handleSubmit = async (e) => {
  //   e.preventDefault();
  //   setErrors('');
  //   setIsSubmitting(true);

  //   const csrfFromCookies = document.cookie
  //     .split('; ')
  //     .find((row) => row.startsWith('csrftoken='))?.split('=')[1];

  //   const tokenToUse = csrfToken || csrfFromCookies;

  //   if (!tokenToUse) {
  //     setErrors('CSRF token missing. Please refresh and try again.');
  //     setIsSubmitting(false);
  //     return;
  //   }

  //   try {
  //     console.log('Sending login request...');
  //     const response = await backendApi.post(
  //       '/system_management_api/login_api/',
  //       { email, password },
  //       {
  //         headers: {
  //           'X-CSRFToken': tokenToUse,
  //           'Content-Type': 'application/json',
  //         },
  //         withCredentials: true,
  //       }
  //     );

  //     console.log('Login response:', response.data);
       
  //     if (response.data.token) {
  // console.log('Login successful!');

  // const token = response.data.token;
  // const user = response.data.user;
  // const artist = response.data.artist; // 👈 IMPORTANT

  // // Store authentication data
  // authLogin(token, tokenToUse);
  // localStorage.setItem('authToken', token);
  // localStorage.setItem('csrfToken', tokenToUse);
  // localStorage.setItem('user', JSON.stringify(user));

  //         router.replace('./dashboard');
  //         console.log('Redirecting to dashboard...');
  //       }

  //     else {
  //       console.log('Login failed:');
  //       setErrors(response.data.message || 'Login failed. Try again.');
  //     }
  //   } catch (err) {
  //     console.error('Login error:', err);
  //     if (err.response) {
  //       setErrors(err.response.data?.message || 'An error occurred during login.');
  //     } else {
  //       setErrors('Network error. Please check your connection.');
  //     }
  //   } finally {
  //     setIsSubmitting(false);
  //   }
  // };

  return (
    <div className="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-sm">
        <h2 className="mt-10 text-center text-2xl font-bold text-gray-900">
          Sign in to your account
        </h2>
      </div>

      <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-900">
              Email address
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-2 block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-400 focus:outline-indigo-600"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-900">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-2 block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-400 focus:outline-indigo-600"
            />
          </div>

          {errors && <p className="text-sm text-red-600">{errors}</p>}

          <button
            type="submit"
            disabled={isSubmitting}
            className={`w-full rounded-md bg-indigo-600 px-3 py-2 text-white hover:bg-indigo-500 ${
              isSubmitting ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {isSubmitting ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  );
}