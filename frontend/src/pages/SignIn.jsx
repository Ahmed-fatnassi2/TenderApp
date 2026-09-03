// import { useState } from 'react';
// import { apiService } from '../services/api';
// import '../styles/SignIn.css';

// function SignIn({ onSignIn, onSignUpClick }) {
//   const [email, setEmail] = useState('');
//   const [password, setPassword] = useState('');
//   const [error, setError] = useState('');
//   const [loading, setLoading] = useState(false);

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     setError('');

//     if (!email || !password) {
//       setError('Please fill in all fields');
//       return;
//     }

//     if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
//       setError('Please enter a valid email');
//       return;
//     }

//     setLoading(true);

//     try {
//       const response = await apiService.login({ email, password });
      
//       // Store user data in localStorage for persistence
//       localStorage.setItem('user', JSON.stringify(response.user));
      
//       // Call parent callback
//       onSignIn(response.user);
      
//       setLoading(false);
//     } catch (err) {
//       setError(err.message || 'Login failed. Please try again.');
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="auth-container">
//       <div className="auth-image-section">
//         <div className="auth-logo">
//           <div className="logo-placeholder">TENDERAPP</div>
//         </div>
//         <div className="auth-image-text">
//           <h2>Government Tender Management</h2>
//           <p>Efficient procurement for public organizations</p>
//         </div>
//       </div>

//       <div className="auth-form-section">
//         <div className="form-card">
//           <div className="form-header">
//             <h1>Sign In</h1>
//             <p>Access your tender dashboard</p>
//           </div>

//           <form onSubmit={handleSubmit} className="auth-form">
//             <div className="form-group">
//               <label htmlFor="email">Email Address</label>
//               <input
//                 id="email"
//                 type="email"
//                 placeholder="your@email.com"
//                 value={email}
//                 onChange={(e) => setEmail(e.target.value)}
//                 disabled={loading}
//                 autoFocus
//               />
//             </div>

//             <div className="form-group">
//               <label htmlFor="password">Password</label>
//               <input
//                 id="password"
//                 type="password"
//                 placeholder="••••••••"
//                 value={password}
//                 onChange={(e) => setPassword(e.target.value)}
//                 disabled={loading}
//               />
//             </div>

//             {error && <div className="error-message">{error}</div>}

//             <button
//               type="submit"
//               className="auth-button"
//               disabled={loading}
//             >
//               {loading ? 'Signing in...' : 'Sign In'}
//             </button>
//           </form>

//           <div className="auth-footer">
//             <p>
//               Don't have an account?{' '}
//               <button 
//                 type="button" 
//                 className="signup-link"
//                 onClick={onSignUpClick}
//               >
//                 Sign Up
//               </button>
//             </p>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }

// export default SignIn;





// components/SignIn.jsx - Updated with Google login

// pages/SignIn.jsx - Update to handle OIDC

import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import SocialLogin from '../pages/SocialLogin';
import '../styles/SignIn.css';

function SignIn({ onSignIn, onSignUpClick }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [isCheckingOIDC, setIsCheckingOIDC] = useState(true);

  // Check if user is already logged in via OIDC
  useEffect(() => {
    const checkOIDC = async () => {
      setIsCheckingOIDC(true);
      try {
        const user = await apiService.checkAuth();
        if (user) {
          onSignIn(user);
        }
      } catch (err) {
        console.error('Error checking OIDC:', err);
      } finally {
        setIsCheckingOIDC(false);
      }
    };
    
    checkOIDC();
  }, [onSignIn]);

  // Handle URL params after OIDC redirect
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const loginSuccess = params.get('login');
    const logoutSuccess = params.get('logout');
    
    if (loginSuccess === 'success') {
      const checkUser = async () => {
        const user = await apiService.checkAuth();
        if (user) {
          onSignIn(user);
        }
      };
      checkUser();
    }
    
    if (logoutSuccess === 'success') {
      localStorage.removeItem('user');
    }
  }, [onSignIn]);


useEffect(() => {
  const checkOIDC = async () => {
    setIsCheckingOIDC(true);
    try {
      // Use the checkAuth method from apiService
      const user = await apiService.checkAuth();
      if (user) {
        onSignIn(user);
      }
    } catch (err) {
      console.error('Error checking OIDC:', err);
    } finally {
      setIsCheckingOIDC(false);
    }
  };
  
  checkOIDC();
}, [onSignIn]);

// Handle URL params after OIDC redirect
useEffect(() => {
  const params = new URLSearchParams(window.location.search);
  const loginSuccess = params.get('login');
  
  if (loginSuccess === 'success') {
    const checkUser = async () => {
      const user = await apiService.checkAuth();
      if (user) {
        onSignIn(user);
      }
    };
    checkUser();
  }
}, [onSignIn]);





  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError('Please enter a valid email');
      return;
    }

    setLoading(true);

    try {
      const response = await apiService.login({ email, password });
      localStorage.setItem('user', JSON.stringify(response.user));
      onSignIn(response.user);
      setLoading(false);
    } catch (err) {
      setError(err.message || 'Login failed. Please try again.');
      setLoading(false);
    }
  };

  if (isCheckingOIDC) {
    return <div className="auth-loading">Loading...</div>;
  }

  return (
    <div className="auth-container">
      <div className="auth-image-section">
        <div className="auth-logo">
          <div className="logo-placeholder">TENDERAPP</div>
        </div>
        <div className="auth-image-text">
          <h2>Government Tender Management</h2>
          <p>Efficient procurement for public organizations</p>
        </div>
      </div>

      <div className="auth-form-section">
        <div className="form-card">
          <div className="form-header">
            <h1>Sign In</h1>
            <p>Access your tender dashboard</p>
          </div>

          <SocialLogin 
            onSuccess={onSignIn}
            onError={(err) => setError(err.message)}
            loading={loading}
          />

          <div className="social-divider">
            <span>or sign in with email</span>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                id="email"
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                autoFocus
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
              />
            </div>

            {error && <div className="error-message">{error}</div>}

            <button
              type="submit"
              className="auth-button"
              disabled={loading}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="auth-footer">
            <p>
              Don't have an account?{' '}
              <button 
                type="button" 
                className="signup-link"
                onClick={onSignUpClick}
              >
                Sign Up
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SignIn;