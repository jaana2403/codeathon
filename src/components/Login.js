import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Login.css";  // Importing the CSS file

const Login = () => {
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://127.0.0.1:5000/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Login failed");

      login(data.user, data.token);

      const redirectMap = { Admin: "/admin", Manager: "/manager", Employee: "/dashboard", CEO: "/ceo" };
      navigate(redirectMap[data.user.position] || "/ceo");
    } catch (error) {
      setError(error.message);
    }
  };

  return (
    <div className="container">
      {/* Header */}
      <header className="header">
        <h1 className="company-name">ANALYTICS PLATFORM</h1>
        <nav>
          <div className="nav-box">
            <Link to="/about" className="nav-link">About</Link>
            <Link to="/achievements" className="nav-link">Achievements</Link>
            <Link to="/help" className="nav-link">Help</Link>
          </div>
        </nav>
      </header>

      {/* Login Box */}
      <div className="login-container">
        <div className="login-box">
          <h2 className="login-title">Employee Login</h2>
          <p className="login-subtitle">
            Or <Link to="/register" className="login-link">Register here...</Link>
          </p>

          <form onSubmit={handleSubmit}>
            {error && <div className="error-box">{error}</div>}

            <input type="email" required className="input-field" placeholder="Email address"
              value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} />

            <input type="password" required className="input-field" placeholder="Password"
              value={formData.password} onChange={(e) => setFormData({ ...formData, password: e.target.value })} />

            <button type="submit" className="login-button">Sign in</button>
          </form>
        </div>
      </div>

      {/* Footer */}
      <footer className="footer">
        <p>Follow us:</p>
        <div className="social-links">
          <a href="#" className="social-link">Facebook</a>
          <a href="#" className="social-link">Twitter</a>
          <a href="#" className="social-link">LinkedIn</a>
        </div>
      </footer>
    </div>
  );
};

export default Login;