import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import AdminDashboard from './AdminDashboard';
import UserDashboard from './UserDashboard';
import Login from './Login';

function Dashboard() {
  const [role, setRole] = useState(null);

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem('user'));
    if (user && user.position) {
      setRole(user.position === 'Admin' ? 'admin' : 'employee');
    }
  }, []);

  if (!role) {
    return <Login setRole={setRole} />;
  }

  return (
    <Routes>
      <Route path="/" element={role === 'admin' ? <AdminDashboard setRole={setRole} /> : <UserDashboard setRole={setRole} />} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default Dashboard;