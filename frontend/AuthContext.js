'use client';

import React, {
  createContext,
  useContext,
  useMemo,
  useState,
  useCallback,
  startTransition,
} from 'react';
import { useRouter } from 'next/navigation';

const AuthContext = createContext(undefined);

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
};

export const AuthProvider = ({ children }) => {
  // Lazy init from localStorage
  const [authToken, setAuthToken] = useState(() => {
    if (typeof window === 'undefined') return null;
    const v = window.localStorage.getItem('authToken');
    return v && v !== 'null' ? v : null;
  });

  const [csrfToken, setCSRFToken] = useState(() => {
    if (typeof window === 'undefined') return null;
    const v = window.localStorage.getItem('csrfToken');
    return v && v !== 'null' ? v : null;
  });

  const router = useRouter();

  const login = useCallback((token, csrf) => {
    if (!token || token === 'null') return;
    setAuthToken(token);
    setCSRFToken(csrf ?? null);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('authToken', token);
      window.localStorage.setItem('csrfToken', csrf ?? '');
    }
  }, []);

  const logout = useCallback(() => {
    setAuthToken(null);
    setCSRFToken(null);
    if (typeof window !== 'undefined') {
      window.localStorage.removeItem('authToken');
      window.localStorage.removeItem('csrfToken');
      window.localStorage.removeItem('user');
    }
    startTransition(() => {
      router.push('/');
    });
  }, [router]);

  const navigate = useCallback((path) => {
    startTransition(() => {
      router.push(path);
    });
  }, [router]);

  const isAuthenticated = !!authToken;

  const value = useMemo(
    () => ({
      authToken,
      csrfToken,
      isAuthenticated,
      login,
      logout,
      navigate,
    }),
    [authToken, csrfToken, isAuthenticated, login, logout, navigate]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};