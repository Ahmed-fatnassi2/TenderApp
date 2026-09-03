// import { useState, useEffect } from 'react';
// import SignIn from './pages/SignIn';
// import SignUp from './pages/SignUp';
// import Dashboard from './pages/Dashboard';
// import Tenders from './pages/Tenders';
// import Scrape from './pages/Scrape';
// import RAGSearch from './pages/RAGSearch';
// import AgentChat from './pages/AgentChat';
// import ITSearch from './pages/ITSearch';
// import Layout from './components/Layout';
// import './styles/globals.css';
// import ScraperSources from './pages/ScraperSources';
// import AddScraperSource from './pages/AddScraperSource';
// import ConstructionAgentChat from './pages/ConstructionAgentChat';
// import AdminDashboard from './pages/AdminDashboard';
// function App() {
//   const [user, setUser] = useState(null);
//   const [activePage, setActivePage] = useState('dashboard');
//   const [authPage, setAuthPage] = useState('signin'); // 'signin' or 'signup'

//   // Check if user is already logged in
//   useEffect(() => {
//     const storedUser = localStorage.getItem('user');
//     if (storedUser) {
//       setUser(JSON.parse(storedUser));
//     }
//   }, []);

//   const handleSignIn = (userData) => {
//     setUser(userData);
//     setActivePage('dashboard');
//   };

//   const handleSignUp = (userData) => {
//     setUser(userData);
//     setActivePage('dashboard');
//   };

//   const handleLogout = () => {
//     setUser(null);
//     localStorage.removeItem('user');
//     setActivePage('dashboard');
//     setAuthPage('signin');
//   };

//   const handleNavigate = (page) => {
//     setActivePage(page);
//   };

//   // Show authentication pages if not logged in
//   if (!user) {
//     return (
//       <>
//         {authPage === 'signin' && (
//           <SignIn 
//             onSignIn={handleSignIn}
//             onSignUpClick={() => setAuthPage('signup')}
//           />
//         )}
//         {authPage === 'signup' && (
//           <SignUp 
//             onSignUp={handleSignUp}
//             onSignInClick={() => setAuthPage('signin')}
//           />
//         )}
//       </>
//     );
//   }

//   // Render main dashboard with layout
//   return (
//     <Layout
//       user={user}
//       onLogout={handleLogout}
//       activePage={activePage}
//       onNavigate={handleNavigate}
//     >
//       {activePage === 'dashboard' && <Dashboard />}
//       {activePage === 'tenders' && <Tenders />}
//       {activePage === 'scrape' && <Scrape />}
//       {activePage === 'rag-search' && <RAGSearch />}
//       {activePage === 'agent' && <AgentChat />}
//       {activePage === 'it-search' && <ITSearch />} 
//       {activePage === 'analytics' && (
//         <div style={{ padding: '2rem' }}>
//           <h2>Analytics</h2>
//           <p>Analytics page coming soon...</p>
//         </div>
//       )}
//       {activePage === 'scraper-sources' && <ScraperSources />}
//       {activePage === 'add-scraper-source' && <AddScraperSource />}
//       {activePage === 'construction-search' && <ConstructionAgentChat />}
//       {activePage === 'admin' && <AdminDashboard />}
//     </Layout>
//   );
// }

// export default App;








import { useState, useEffect } from 'react';
import SignIn from './pages/SignIn';
import SignUp from './pages/SignUp';
import Dashboard from './pages/Dashboard';
import Tenders from './pages/Tenders';
import Scrape from './pages/Scrape';
import RAGSearch from './pages/RAGSearch';
import AgentChat from './pages/AgentChat';
import ITSearch from './pages/ITSearch';
import Layout from './components/Layout';
import './styles/globals.css';
import ScraperSources from './pages/ScraperSources';
import AddScraperSource from './pages/AddScraperSource';
import ConstructionAgentChat from './pages/ConstructionAgentChat';
import AdminDashboard from './pages/AdminDashboard';
import { apiService } from './services/api';
import NotificationSettings from './pages/NotificationSettings';
function App() {
  const [user, setUser] = useState(null);
  const [activePage, setActivePage] = useState('dashboard');
  const [authPage, setAuthPage] = useState('signin');
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is already logged in
  useEffect(() => {
    const checkAuth = async () => {
      setIsLoading(true);
      try {
        // First check localStorage for email/password auth
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
          setUser(JSON.parse(storedUser));
          setIsLoading(false);
          return;
        }
        
        // Then check OIDC session
        const oidcStatus = await apiService.checkOIDCAuth();
        if (oidcStatus && oidcStatus.authenticated) {
          const oidcUser = await apiService.getOIDCUser();
          if (oidcUser && oidcUser.id) {
            localStorage.setItem('user', JSON.stringify(oidcUser));
            setUser(oidcUser);
          }
        }
      } catch (error) {
        console.error('Error checking auth:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    checkAuth();
  }, []);

  // Handle OIDC redirect params
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const loginSuccess = params.get('login');
    const logoutSuccess = params.get('logout');
    const code = params.get('code');
    
    if (loginSuccess === 'success' || code) {
      // User authenticated via OIDC
      const getOIDCUser = async () => {
        try {
          const oidcUser = await apiService.getOIDCUser();
          if (oidcUser && oidcUser.id) {
            localStorage.setItem('user', JSON.stringify(oidcUser));
            setUser(oidcUser);
            setActivePage('dashboard');
          }
        } catch (error) {
          console.error('Error getting OIDC user:', error);
        }
      };
      getOIDCUser();
    }
    
    if (logoutSuccess === 'success') {
      localStorage.removeItem('user');
      setUser(null);
      setAuthPage('signin');
    }
  }, []);

  const handleSignIn = (userData) => {
    setUser(userData);
    setActivePage('dashboard');
  };

  const handleSignUp = (userData) => {
    setUser(userData);
    setActivePage('dashboard');
  };

const handleLogout = async () => {
  try {
    // Call the regular logout endpoint first
    await apiService.logout();
  } catch (error) {
    console.error('Logout error:', error);
  }
  
  // Always clear the session on the frontend
  setUser(null);
  localStorage.removeItem('user');
  setActivePage('dashboard');
  setAuthPage('signin');
  
  // If user was logged in via Google, redirect to Google logout
  const storedUser = localStorage.getItem('user');
  if (storedUser) {
    try {
      const userData = JSON.parse(storedUser);
      if (userData.provider && userData.provider !== 'local') {
        // Redirect to OIDC logout (which clears session and redirects back)
        window.location.href = 'http://localhost:5000/auth/oidc/logout';
        return;
      }
    } catch (e) {
      // Ignore
    }
  }
  
  // Regular logout redirect
  window.location.href = '/signin';
};

  const handleNavigate = (page) => {
    setActivePage(page);
  };

  if (isLoading) {
    return <div className="auth-loading">Loading...</div>;
  }

  // Show authentication pages if not logged in
  if (!user) {
    return (
      <>
        {authPage === 'signin' && (
          <SignIn 
            onSignIn={handleSignIn}
            onSignUpClick={() => setAuthPage('signup')}
          />
        )}
        {authPage === 'signup' && (
          <SignUp 
            onSignUp={handleSignUp}
            onSignInClick={() => setAuthPage('signin')}
          />
        )}
      </>
    );
  }

  // Render main dashboard with layout
  return (
    <Layout
      user={user}
      onLogout={handleLogout}
      activePage={activePage}
      onNavigate={handleNavigate}
    >
      {activePage === 'dashboard' && <Dashboard onNavigate={handleNavigate} />}
      {activePage === 'tenders' && <Tenders />}
      {activePage === 'scrape' && <Scrape />}
      {activePage === 'rag-search' && <RAGSearch />}
      {activePage === 'agent' && <AgentChat />}
      {activePage === 'it-search' && <ITSearch />} 
      {activePage === 'analytics' && (
        <div style={{ padding: '2rem' }}>
          <h2>Analytics</h2>
          <p>Analytics page coming soon...</p>
        </div>
      )}
      {activePage === 'scraper-sources' && <ScraperSources />}
      {activePage === 'add-scraper-source' && <AddScraperSource />}
      {activePage === 'construction-search' && <ConstructionAgentChat />}
      {activePage === 'admin' && <AdminDashboard />}
      {activePage === 'notification-settings' && <NotificationSettings />}
    </Layout>
  );
}

export default App;