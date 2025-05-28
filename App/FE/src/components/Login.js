// src/components/Login.js
import React, { useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";
import "./Auth.css";

const Login = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [message, setMessage] = useState("");

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post("http://localhost:5000/api/login", form);
      localStorage.setItem("access_token", res.data.access_token);
      localStorage.setItem("user_id", res.data.user_id);
      navigate("/dashboard");
    } catch (err) {
      setMessage(err.response?.data?.msg || "Login failed");
    }
  };

  return (
    <div className="auth-container slide-in">
      <h2>Login</h2>
      <form onSubmit={onSubmit}>
        <label>Username:</label>
        <input
          name="username"
          value={form.username}
          onChange={onChange}
          required
        />
        <label>Password:</label>
        <input
          name="password"
          type="password"
          value={form.password}
          onChange={onChange}
          required
        />
        <button type="submit" className="btn">
          Login
        </button>
      </form>
      {message && <p className="message">{message}</p>}
      <p>
        Don't have an account? <Link to="/register">Register here</Link>.
      </p>
    </div>
  );
};

export default Login;
