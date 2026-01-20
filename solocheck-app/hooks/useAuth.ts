import { useEffect } from 'react';
import { useAuthStore } from '@/stores/auth.store';

/**
 * Custom hook for authentication functionality
 * Provides easy access to auth state and actions
 */
export function useAuth() {
  const {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    checkAuth,
    updateUser,
    clearError,
  } = useAuthStore();

  // Check auth status on mount
  useEffect(() => {
    if (!isAuthenticated && !isLoading) {
      checkAuth();
    }
  }, []);

  return {
    // State
    user,
    isAuthenticated,
    isLoading,
    error,

    // Actions
    login,
    register,
    logout,
    checkAuth,
    updateUser,
    clearError,

    // Computed
    isLoggedIn: isAuthenticated && !!user,
  };
}

export default useAuth;
