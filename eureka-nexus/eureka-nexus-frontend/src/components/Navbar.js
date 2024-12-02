import React, { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import jwt_decode from "jwt-decode";
import logo from "../assets/images/Logo.png";

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem("token"));
  const [username, setUsername] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      const userdata = jwt_decode(token);
      if (userdata) {
        setUsername(userdata.username);
      }
    }
    setIsLoggedIn(!!localStorage.getItem("token"));
  }, [location.pathname]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("userdata");
    localStorage.setItem("logoutMessage", "You have been logged out successfully");
    setIsLoggedIn(false);
    setUsername("");
    navigate("/");
  };

  return ( // Ensure the return statement is inside the Navbar function
    <nav className="navbar navbar-expand-lg" style={{ backgroundColor: 'var(--background-gray)' }}>
      <div className="container">
        <Link className="navbar-brand" to="/" style={{ color: 'var(--primary-text-gray)' }}>
          <img src={logo} alt="Eureka Nexus Logo" style={{ height: '40px' }} />
        </Link>

        <div className="collapse navbar-collapse justify-content-end">
          <div className="navbar-nav">
            {isLoggedIn && (
              <Link className="nav-link btn btn-primary text-white me-2" to="/post-mystery" style={{ backgroundColor: 'var(--primary-blue)' }}>
                Find the object
              </Link>
            )}
            {isLoggedIn ? (
              <>
                <Link className="nav-link" to="/profile" style={{ color: 'var(--primary-text-gray)' }}>
                  {username}
                </Link>
                <button className="nav-link btn btn-link" style={{ color: 'var(--primary-text-gray)' }} onClick={handleLogout}>
                  Logout
                </button>
              </>
            ) : null} {/* Add a fallback to prevent JSX error */}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
