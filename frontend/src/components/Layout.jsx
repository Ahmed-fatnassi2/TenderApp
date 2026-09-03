import Navbar from './Navbar';
import Sidebar from './Sidebar';
import '../styles/Layout.css';

function Layout({ user, onLogout, activePage, onNavigate, children }) {
  return (
    <div className="layout">
      <div className="layout-sidebar">
        <Sidebar activePage={activePage} onNavigate={onNavigate} />
      </div>
      <div className="layout-main">
        <div className="layout-navbar">
          <Navbar user={user} onLogout={onLogout} />
        </div>
        <div className="layout-content">
          {children}
        </div>
      </div>
    </div>
  );
}

export default Layout;
