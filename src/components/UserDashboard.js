import React, { useState, useEffect } from "react";
import axios from "axios";
import * as XLSX from "xlsx";
import { useNavigate } from "react-router-dom";
import "./UserDashboard.css";

const UserDashboard = () => {
  const [selectedOption, setSelectedOption] = useState("");
  const [data, setData] = useState([]);
  const [editingItem, setEditingItem] = useState(null);
  const [editName, setEditName] = useState("");
  const navigate = useNavigate();

  const userOptions = ["Create Vendor", "Manage Vendor", "Create Location", "Manage Location"];

  useEffect(() => {
    if (selectedOption.includes("Manage")) {
      fetchData();
    }
  }, [selectedOption]);

  const getAuthHeaders = () => {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Authentication required. Redirecting to login.");
      navigate("/login");
      return null;
    }
    return { headers: { Authorization: `Bearer ${token}` } };
  };

  const fetchData = async () => {
    if (!selectedOption.includes("Manage")) return;

    const entity = selectedOption.replace("Manage ", "").toLowerCase();
    const headers = getAuthHeaders();
    if (!headers) return;

    try {
      const response = await axios.get(
        `http://localhost:5000/api/manage_${entity}`, // Ensure this exists in login.py
        headers
      );
      setData(response.data);
    } catch (error) {
      console.error("Error fetching data:", error);
      handleAuthError(error);
    }
  };

  const handleCreate = async () => {
    const entity = selectedOption.replace("Create ", "").toLowerCase();
    const headers = getAuthHeaders();
    if (!headers) return;

    const name = prompt(`Enter ${entity} name:`);
    if (!name) return;

    try {
      const response = await axios.post(
        `http://localhost:5000/api/create_${entity}`, // Check login.py for this route
        { name },
        headers
      );
      alert(response.data.message || "Successfully created!");
      fetchData();
    } catch (error) {
      console.error("Error creating item:", error);
      alert(error.response?.data?.error || "An error occurred. Please try again.");
      handleAuthError(error);
    }
  };

  const handleEdit = async (id) => {
    if (!editingItem) {
      const item = data.find((item) => item.id === id);
      setEditingItem(id);
      setEditName(item.name);
      return;
    }

    const entity = selectedOption.replace("Manage ", "").toLowerCase();
    const headers = getAuthHeaders();
    if (!headers) return;

    try {
      const response = await axios.put(
        `http://localhost:5000/api/update_${entity}`,
        { id, name: editName },
        headers
      );
      alert(response.data.message);
      setEditingItem(null);
      setEditName("");
      fetchData();
    } catch (error) {
      console.error("Error updating item:", error);
      handleAuthError(error);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this item?")) return;

    const entity = selectedOption.replace("Manage ", "").toLowerCase();
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

  const handleExportToExcel = () => {
    const entity = selectedOption.split(" ")[1];
    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, entity);
    XLSX.writeFile(wb, `${entity}_data.xlsx`);
  };

  const handleImportFromExcel = async (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();
    const headers = getAuthHeaders();
    if (!headers) return;

    reader.onload = async (e) => {
      const data = new Uint8Array(e.target.result);
      const workbook = XLSX.read(data, { type: "array" });
      const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
      const jsonData = XLSX.utils.sheet_to_json(firstSheet);

      const entity = selectedOption.replace("Manage ", "").toLowerCase();

      try {
        const response = await axios.post(
          `http://localhost:5000/api/bulk_create_${entity}`,
          { data: jsonData },
          headers
        );
        alert(response.data.message);
        fetchData();
      } catch (error) {
        console.error("Error importing data:", error);
        handleAuthError(error);
      }
    };

    reader.readAsArrayBuffer(file);
  };

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
        <h2>User Dashboard</h2>
        <select
          onChange={(e) => setSelectedOption(e.target.value)}
          value={selectedOption}
          className="select-option"
        >
          <option value="">Select an option</option>
          {userOptions.map((option, index) => (
            <option key={index} value={option}>
              {option}
            </option>
          ))}
        </select>

        <button
          disabled={!selectedOption}
          onClick={selectedOption.includes("Create") ? handleCreate : fetchData}
          className="action-button"
        >
          {selectedOption.includes("Create") ? "Create" : "Load Data"}
        </button>

        {selectedOption.includes("Manage") && (
          <div className="data-list">
            <div className="list-header">
              <h3>Existing {selectedOption.split(" ")[1]}</h3>
              <div className="excel-actions">
                <button onClick={handleExportToExcel} className="excel-button">
                  Export to Excel
                </button>
                <input
                  type="file"
                  accept=".xlsx, .xls"
                  onChange={handleImportFromExcel}
                  className="file-input"
                  id="excel-upload"
                />
                <label htmlFor="excel-upload" className="excel-button">
                  Import from Excel
                </label>
              </div>
            </div>
            <ul>
              {data.map((item, index) => (
                <li key={index} className="list-item">
                  {editingItem === item.id ? (
                    <input
                      type="text"
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      className="edit-input"
                    />
                  ) : (
                    <span>{item.name}</span>
                  )}
                  <div className="item-actions">
                    <button onClick={() => handleEdit(item.id)} className="edit-button">
                      {editingItem === item.id ? "Save" : "Edit"}
                    </button>
                    <button onClick={() => handleDelete(item.id)} className="delete-button">
                      Delete
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserDashboard;