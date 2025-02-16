import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './admin.css';

const AdminDashboard = () => {
    return (
      <div >
        <h1>Admin Panel</h1>
        <ul>
          <li><Link to="#">Manage Organizations</Link></li>
          <li><Link to="#">Manage Facilities</Link></li>
          <li><Link to="#">Manage Vendors</Link></li>
          <li><Link to="#">Manage BCM Users</Link></li>
        </ul>
      </div>
    );
  };

export default AdminDashboard;
  