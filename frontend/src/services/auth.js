// services/auth.js
const API_BASE_URL = 'http://localhost:5000';

export const authService = {
  // Check if user is authenticated
  async checkAuth() {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/status`, {
        credentials: 'include'
      });
      const data = await response.json();
      return data.authenticated;
    } catch {
      return false;
    }
  },

  // Get current user
  async getCurrentUser() {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/user`, {
        credentials: 'include'
      });
      return await response.json();
    } catch {
      return null;
    }
  },

  // Login - redirects to OIDC provider
  login(provider = 'google') {
    window.location.href = `${API_BASE_URL}/auth/login?provider=${provider}`;
  },

  // Logout
  logout() {
    window.location.href = `${API_BASE_URL}/auth/logout`;
  }
};