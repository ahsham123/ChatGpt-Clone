import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

function NavBar() {
  const navigate = useNavigate();
  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };
  return (
    <nav className="navbar navbar-light bg-light mb-4">
      <div className="container">
        <Link className="navbar-brand" to="/chat">
          ChatGPT Clone
        </Link>
        <div>
          <Link className="btn btn-outline-primary me-2" to="/chat">
            Chat
          </Link>
          <Link className="btn btn-outline-secondary me-2" to="/history">
            History
          </Link>
          <button className="btn btn-outline-danger" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}

export default NavBar;