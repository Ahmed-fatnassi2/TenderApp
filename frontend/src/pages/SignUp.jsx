// import { useState } from 'react';
// import { apiService } from '../services/api';
// import '../styles/SignUp.css';

// function SignUp({ onSignUp, onSignInClick }) {
//   const [formData, setFormData] = useState({
//     username: '',
//     firstName: '',
//     lastName: '',
//     email: '',
//     password: '',
//     confirmPassword: '',
//   });
//   const [error, setError] = useState('');
//   const [loading, setLoading] = useState(false);

//   const handleChange = (e) => {
//     // Auto-generate username from email if not manually set
//     if (e.target.name === 'email' && !formData.username) {
//       const username = e.target.value.split('@')[0];
//       setFormData({
//         ...formData,
//         [e.target.name]: e.target.value,
//         username: username,
//       });
//     } else {
//       setFormData({
//         ...formData,
//         [e.target.name]: e.target.value,
//       });
//     }
//   };

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     setError('');

//     // Validation
//     if (!formData.firstName || !formData.lastName || !formData.email || 
//         !formData.password || !formData.confirmPassword || !formData.username) {
//       setError('Please fill in all fields');
//       return;
//     }

//     if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
//       setError('Please enter a valid email');
//       return;
//     }

//     if (formData.username.length < 3) {
//       setError('Username must be at least 3 characters');
//       return;
//     }

//     if (formData.password.length < 6) {
//       setError('Password must be at least 6 characters');
//       return;
//     }

//     if (formData.password !== formData.confirmPassword) {
//       setError('Passwords do not match');
//       return;
//     }

//     setLoading(true);

//     try {
//       const response = await apiService.register({
//         username: formData.username,
//         firstName: formData.firstName,
//         lastName: formData.lastName,
//         email: formData.email,
//         password: formData.password,
//       });

//       // Store user data
//       localStorage.setItem('user', JSON.stringify(response.user));
      
//       // Call parent callback
//       onSignUp(response.user);
      
//       setLoading(false);
//     } catch (err) {
//       setError(err.message || 'Registration failed. Please try again.');
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
//           <h2>Join the Network</h2>
//           <p>Create an account to manage government tenders</p>
//         </div>
//       </div>

//       <div className="auth-form-section">
//         <div className="form-card">
//           <div className="form-header">
//             <h1>Create Account</h1>
//             <p>Sign up to get started</p>
//           </div>

//           <form onSubmit={handleSubmit} className="auth-form">
//             <div className="form-group">
//               <label htmlFor="username">Username</label>
//               <input
//                 id="username"
//                 type="text"
//                 name="username"
//                 placeholder="johndoe"
//                 value={formData.username}
//                 onChange={handleChange}
//                 disabled={loading}
//               />
//               <small>This will be your unique identifier</small>
//             </div>

//             <div className="form-row">
//               <div className="form-group">
//                 <label htmlFor="firstName">First Name</label>
//                 <input
//                   id="firstName"
//                   type="text"
//                   name="firstName"
//                   placeholder="John"
//                   value={formData.firstName}
//                   onChange={handleChange}
//                   disabled={loading}
//                 />
//               </div>

//               <div className="form-group">
//                 <label htmlFor="lastName">Last Name</label>
//                 <input
//                   id="lastName"
//                   type="text"
//                   name="lastName"
//                   placeholder="Doe"
//                   value={formData.lastName}
//                   onChange={handleChange}
//                   disabled={loading}
//                 />
//               </div>
//             </div>

//             <div className="form-group">
//               <label htmlFor="email">Email Address</label>
//               <input
//                 id="email"
//                 type="email"
//                 name="email"
//                 placeholder="your@email.com"
//                 value={formData.email}
//                 onChange={handleChange}
//                 disabled={loading}
//               />
//             </div>

//             <div className="form-group">
//               <label htmlFor="password">Password</label>
//               <input
//                 id="password"
//                 type="password"
//                 name="password"
//                 placeholder="••••••••"
//                 value={formData.password}
//                 onChange={handleChange}
//                 disabled={loading}
//               />
//               <small>At least 6 characters</small>
//             </div>

//             <div className="form-group">
//               <label htmlFor="confirmPassword">Confirm Password</label>
//               <input
//                 id="confirmPassword"
//                 type="password"
//                 name="confirmPassword"
//                 placeholder="••••••••"
//                 value={formData.confirmPassword}
//                 onChange={handleChange}
//                 disabled={loading}
//               />
//             </div>

//             {error && <div className="error-message">{error}</div>}

//             <button
//               type="submit"
//               className="auth-button"
//               disabled={loading}
//             >
//               {loading ? 'Creating account...' : 'Sign Up'}
//             </button>
//           </form>

//           <div className="auth-footer">
//             <p>
//               Already have an account?{' '}
//               <button 
//                 type="button" 
//                 className="signin-link"
//                 onClick={onSignInClick}
//               >
//                 Sign In
//               </button>
//             </p>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }

// export default SignUp;






// components/pages/SignUp.jsx - Updated with Google OIDC

import { useState } from 'react';
import { apiService } from '../services/api';
import SocialLogin from '../pages/SocialLogin';
import '../styles/SignUp.css';

function SignUp({ onSignUp, onSignInClick }) {
  const [formData, setFormData] = useState({
    username: '',
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    if (e.target.name === 'email' && !formData.username) {
      const username = e.target.value.split('@')[0];
      setFormData({
        ...formData,
        [e.target.name]: e.target.value,
        username: username,
      });
    } else {
      setFormData({
        ...formData,
        [e.target.name]: e.target.value,
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.firstName || !formData.lastName || !formData.email || 
        !formData.password || !formData.confirmPassword || !formData.username) {
      setError('Please fill in all fields');
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      setError('Please enter a valid email');
      return;
    }

    if (formData.username.length < 3) {
      setError('Username must be at least 3 characters');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      const response = await apiService.register({
        username: formData.username,
        firstName: formData.firstName,
        lastName: formData.lastName,
        email: formData.email,
        password: formData.password,
      });

      localStorage.setItem('user', JSON.stringify(response.user));
      onSignUp(response.user);
      setLoading(false);
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-image-section">
        <div className="auth-logo">
          <div className="logo-placeholder">TENDERAPP</div>
        </div>
        <div className="auth-image-text">
          <h2>Join the Network</h2>
          <p>Create an account to manage government tenders</p>
        </div>
      </div>

      <div className="auth-form-section">
        <div className="form-card">
          <div className="form-header">
            <h1>Create Account</h1>
            <p>Sign up to get started</p>
          </div>

          {/* Google OIDC Sign Up */}
          <SocialLogin 
            onSuccess={onSignUp}
            onError={(err) => setError(err.message)}
            loading={loading}
          />

          <div className="social-divider">
            <span>or sign up with email</span>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                type="text"
                name="username"
                placeholder="johndoe"
                value={formData.username}
                onChange={handleChange}
                disabled={loading}
              />
              <small>This will be your unique identifier</small>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="firstName">First Name</label>
                <input
                  id="firstName"
                  type="text"
                  name="firstName"
                  placeholder="John"
                  value={formData.firstName}
                  onChange={handleChange}
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="lastName">Last Name</label>
                <input
                  id="lastName"
                  type="text"
                  name="lastName"
                  placeholder="Doe"
                  value={formData.lastName}
                  onChange={handleChange}
                  disabled={loading}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                id="email"
                type="email"
                name="email"
                placeholder="your@email.com"
                value={formData.email}
                onChange={handleChange}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                name="password"
                placeholder="••••••••"
                value={formData.password}
                onChange={handleChange}
                disabled={loading}
              />
              <small>At least 6 characters</small>
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                id="confirmPassword"
                type="password"
                name="confirmPassword"
                placeholder="••••••••"
                value={formData.confirmPassword}
                onChange={handleChange}
                disabled={loading}
              />
            </div>

            {error && <div className="error-message">{error}</div>}

            <button
              type="submit"
              className="auth-button"
              disabled={loading}
            >
              {loading ? 'Creating account...' : 'Sign Up'}
            </button>
          </form>

          <div className="auth-footer">
            <p>
              Already have an account?{' '}
              <button 
                type="button" 
                className="signin-link"
                onClick={onSignInClick}
              >
                Sign In
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SignUp;