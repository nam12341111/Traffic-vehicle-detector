import React from "react";
import { Link } from "react-router-dom";
import "./Home.css";

const Home = () => {
  return (
    <div className="home-container fade-in">
      <h1>Welcome to YOLO Detector</h1>
      <p>Upload your images and see real-time vehicle detection results.</p>
      <div className="home-buttons">
        <Link to="/login" className="btn">
          Login
        </Link>
        <Link to="/register" className="btn">
          Register
        </Link>
      </div>
    </div>
  );
};

export default Home;
