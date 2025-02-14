import React, { useState } from "react";
import "./UserDashboard.css";

const UserDashboard = () => {
  const [selectedOption, setSelectedOption] = useState("");

  const userOptions = [
    "Create Vendor",
    "Manage Vendor",
    "Create Location",
    "Manage Location"
  ];

  return (
    <div className="dashboard-container">
      <div className="dashboard-card">
        <h2>User Dashboard</h2>
        <select onChange={(e) => setSelectedOption(e.target.value)} value={selectedOption}>
          <option value="">Select an option</option>
          {userOptions.map((option, index) => (
            <option key={index} value={option}>
              {option}
            </option>
          ))}
        </select>
        <button disabled={!selectedOption}>Proceed</button>
      </div>
    </div>
  );
};

export default UserDashboard;
