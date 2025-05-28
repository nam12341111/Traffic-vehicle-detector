"use client";

// src/components/Dashboard.js

import { useState, useEffect } from "react";
import axios from "axios";
import "./Dashboard.css";

const Dashboard = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isVideo, setIsVideo] = useState(false);
  const [historyItems, setHistoryItems] = useState([]);
  const [message, setMessage] = useState("");
  const [latestResult, setLatestResult] = useState(null);
  const [latestIsVideo, setLatestIsVideo] = useState(false);

  const token = localStorage.getItem("access_token");
  const API_BASE = "http://localhost:5000/api";

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API_BASE}/history`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      console.log("History API response:", res.data);
      const itemsWithType = res.data.map((item) => {
        if (!item.type) {
          const ext = item.result_filename.split(".").pop().toLowerCase();
          return {
            ...item,
            type: ["mp4", "avi", "mov", "mkv"].includes(ext)
              ? "video"
              : "image",
          };
        }
        return item;
      });
      console.log("Parsed history items:", itemsWithType);
      setHistoryItems(itemsWithType);
    } catch (err) {
      console.error("Failed to fetch history", err);
    }
  };

  const getMediaUrl = (filename, type) => {
    if (type === "video") {
      return `${API_BASE}/video/${filename}`;
    } else {
      return `http://localhost:5000/uploads/results/${filename}`;
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    console.log("Selected file:", file);
    setSelectedFile(file);
    setIsVideo(file && file.type.startsWith("video/"));
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append(isVideo ? "video" : "image", selectedFile);

    const url = isVideo ? `${API_BASE}/upload_video` : `${API_BASE}/upload`;

    try {
      console.log(`Uploading to ${url}`, selectedFile);
      const res = await axios.post(url, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          Authorization: `Bearer ${token}`,
        },
      });
      console.log("Upload response:", res.data);

      setMessage(res.data.msg || "Upload succeeded");

      const resultPath = getMediaUrl(
        res.data.result_filename,
        isVideo ? "video" : "image"
      );
      console.log("Result URL:", resultPath);
      setLatestResult(resultPath);
      setLatestIsVideo(isVideo);

      setSelectedFile(null);
      setIsVideo(false);

      fetchHistory();
    } catch (err) {
      console.error("Upload failed", err);
      setMessage("Upload failed: " + (err.response?.data?.msg || err.message));
    }
  };

  const handleMediaClick = (url) => {
    console.log("Opening media URL:", url);
    window.open(url, "_blank");
  };

  return (
    <div className="dashboard-container fade-in">
      <h2>Dashboard</h2>

      <form onSubmit={handleUpload} className="upload-form">
        <input
          type="file"
          onChange={handleFileChange}
          accept="image/*,video/*"
          required
        />
        <button type="submit" className="btn">
          Upload & Detect
        </button>
      </form>

      {message && <p className="message">{message}</p>}

      {latestResult && (
        <div className="latest-result">
          <h3>Latest Detection Result</h3>
          <a
            href={latestResult}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => {
              e.preventDefault();
              handleMediaClick(latestResult);
            }}
          >
            {latestIsVideo ? (
              <video controls style={{ maxWidth: "100%" }}>
                <source src={latestResult} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            ) : (
              <img
                src={latestResult || "/placeholder.svg"}
                alt="Latest detection result"
                style={{ maxWidth: "100%" }}
              />
            )}
          </a>
        </div>
      )}

      <hr />

      <h3>Your Upload History</h3>
      <div className="history-grid">
        {historyItems.length === 0 && <p>No history yet.</p>}
        {historyItems.map((item) => {
          const url = getMediaUrl(item.result_filename, item.type);
          return (
            <div key={item.id} className="history-card">
              <a
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => {
                  e.preventDefault();
                  handleMediaClick(url);
                }}
              >
                {item.type === "video" ? (
                  <video controls style={{ maxWidth: "100%" }}>
                    <source src={url} type="video/mp4" />
                    Your browser does not support the video tag.
                  </video>
                ) : (
                  <img
                    src={url || "/placeholder.svg"}
                    alt={item.original_filename}
                    style={{ maxWidth: "100%" }}
                  />
                )}
              </a>
              <p>{item.timestamp}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Dashboard;
