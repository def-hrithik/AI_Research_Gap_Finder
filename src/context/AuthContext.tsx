import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { User, AuthCredentials, SignupDetails } from '../types/auth';

interface AuthContextType {
  user: User | null;
  isAuthLoading: boolean;
  login: (credentials: AuthCredentials) => Promise<User>;
  signup: (details: SignupDetails) => Promise<User>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);
const STORAGE_KEY = 'rgf_mock_user';
const MOCK_DELAY = 700;

const delay = (ms: number) => new Promise((res) => setTimeout(res, ms));

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthLoading, setIsAuthLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        setUser(JSON.parse(stored));
      } catch {
        localStorage.removeItem(STORAGE_KEY);
      }
    }
    setIsAuthLoading(false);
  }, []);

  const login = useCallback(async ({ email, password }: AuthCredentials): Promise<User> => {
    await delay(MOCK_DELAY);

    if (!email.trim() || !password.trim()) {
      throw new Error('Email and password are required.');
    }
    if (!/^\S+@\S+\.\S+$/.test(email)) {
      throw new Error('Enter a valid email address.');
    }
    if (password.length < 6) {
      throw new Error('Incorrect email or password.');
    }

    // Mock backend: any well-formed email/password combination succeeds.
    const mockUser: User = {
      id: `user-${btoa(email).slice(0, 8)}`,
      name: email.split('@')[0].replace(/[._-]/g, ' '),
      email,
    };

    localStorage.setItem(STORAGE_KEY, JSON.stringify(mockUser));
    setUser(mockUser);
    return mockUser;
  }, []);

  const signup = useCallback(async ({ name, email, password }: SignupDetails): Promise<User> => {
    await delay(MOCK_DELAY);

    if (!name.trim()) {
      throw new Error('Name is required.');
    }
    if (!/^\S+@\S+\.\S+$/.test(email)) {
      throw new Error('Enter a valid email address.');
    }
    if (password.length < 6) {
      throw new Error('Password must be at least 6 characters.');
    }

    const mockUser: User = {
      id: `user-${btoa(email).slice(0, 8)}`,
      name,
      email,
    };

    localStorage.setItem(STORAGE_KEY, JSON.stringify(mockUser));
    setUser(mockUser);
    return mockUser;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, isAuthLoading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
