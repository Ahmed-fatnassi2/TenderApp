import { useState } from 'react';
import '../styles/Navbar.css';

function Navbar({ user, onLogout }) {
  const [showMenu, setShowMenu] = useState(false);

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <h1>TenderApp</h1>
        </div>

        <div className="navbar-center">
          <span className="navbar-info">Government Tender Portal</span>
        </div>

        <div className="navbar-user">
          <div className="user-info">
            <span className="user-name">{user?.first_name || 'User'}</span>
            <span className="user-email">{user?.email}</span>
          </div>

          <div className="user-menu">
            <button
              className="menu-trigger"
              onClick={() => setShowMenu(!showMenu)}
            >
              ⋮
            </button>
            {showMenu && (
              <div className="dropdown-menu">
                <button className="dropdown-item">Profile</button>
                <button className="dropdown-item">Settings</button>
                <hr />
                <button className="dropdown-item logout" onClick={onLogout}>
                  Sign Out
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
