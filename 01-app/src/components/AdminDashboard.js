import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom"; // For redirection
import "./AdminDashboard.css";

const AdminDashboard = () => {
  const [selectedOption, setSelectedOption] = useState("");
  const [data, setData] = useState([]);
  const navigate = useNavigate(); // Redirect for authentication failure

  const adminOptions = [
    "Create Organization",
    "Manage Organization",
    "Create Org Group",
    "Manage Org Group",
    "Create Business Unit",
    "Manage Business Unit",
    "Create Subfunction",
    "Manage Subfunction",
    "Create Faculties",
    "Manage Faculties",
  ];

  useEffect(() => {
    if (selectedOption.includes("Manage")) {
      fetchData();
    }
  }, [selectedOption]);

  // Get authentication headers
  const getAuthHeaders = () => {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Authentication required. Redirecting to login.");
      navigate("/login");
      return null;
    }
    return { headers: { Authorization: `Bearer ${token}` } };
  };

  // Fetch data (Manage option)
  const fetchData = async () => {
    if (!selectedOption.includes("Manage")) return;

    const entity = selectedOption.replace("Manage ", "").replace(/ /g, "_").toLowerCase();
    const headers = getAuthHeaders();
    if (!headers) return;

    try {
      const response = await axios.get(
        `http://localhost:5000/api/manage_${entity}`,
        headers
      );
      setData(response.data);
    } catch (error) {
      console.error("Error fetching data:", error);
      handleAuthError(error);
    }
  };

  // Create entity
  const handleCreate = async () => {
    const entity = selectedOption.replace("Create ", "").replace(/ /g, "_").toLowerCase();
    const headers = getAuthHeaders();
    if (!headers) return;

    let payload = {};
    if (entity === "subfunction") {
      const id = prompt("Enter ID:");
      const business_unit_id = prompt("Enter Business Unit ID:");
      const name = prompt("Enter Name:");
      if (!id || !business_unit_id || !name) return;
      payload = { id, business_unit_id, name };
    } else {
      const name = prompt(`Enter ${selectedOption.split(" ")[1]} Name:`);
      if (!name) return;
      payload = { name };
    }

    try {
      const response = await axios.post(
        `http://localhost:5000/api/create_${entity}`,
        payload,
        headers
      );
      alert(response.data.message);
      fetchData();
    } catch (error) {
      console.error("Error creating item:", error);
      handleAuthError(error);
    }
  };

  // Delete entity
  const handleDelete = async (id) => {
    const entity = selectedOption.replace("Manage ", "").replace(/ /g, "_").toLowerCase();
    const headers = getAuthHeaders();
    if (!headers) return;

    try {
      const response = await axios.delete(
        `http://localhost:5000/api/delete_${entity}`,
        { data: { id }, ...headers }
      );
      alert(response.data.message);
      fetchData();
    } catch (error) {
      console.error("Error deleting item:", error);
      handleAuthError(error);
    }
  };

  // Handle authentication errors
  const handleAuthError = (error) => {
    if (error.response && error.response.status === 401) {
      alert("Session expired. Please log in again.");
      localStorage.removeItem("token");
      navigate("/login");
    } else {
      alert("An error occurred. Please try again.");
    }
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-card">
        <h2>Admin Dashboard</h2>
        <select onChange={(e) => setSelectedOption(e.target.value)} value={selectedOption}>
          <option value="">Select an option</option>
          {adminOptions.map((option, index) => (
            <option key={index} value={option}>
              {option}
            </option>
          ))}
        </select>
        <button disabled={!selectedOption} onClick={selectedOption.includes("Create") ? handleCreate : fetchData}>
          {selectedOption.includes("Create") ? "Create" : "Load Data"}
        </button>
        {selectedOption.includes("Manage") && (
          <div className="data-list">
            <h3>Existing {selectedOption.split(" ")[1]}</h3>
            <ul>
              {data.map((item, index) => (
                <li key={index}>
                  {item.name} <button onClick={() => handleDelete(item.id)}>Delete</button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
