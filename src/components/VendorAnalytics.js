import React, { useState, useEffect } from "react";
import { PieChart, Pie, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from "recharts";

const VendorAnalytics = ({ vendors }) => {
  const [categoryData, setCategoryData] = useState([]);
  const [monthlyData, setMonthlyData] = useState([]);

  // Colors for charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658'];

  useEffect(() => {
    if (vendors && vendors.length > 0) {
      // Generate category distribution data
      const categories = {};
      vendors.forEach(vendor => {
        const category = vendor.category || 'Uncategorized';
        if (categories[category]) {
          categories[category] += 1;
        } else {
          categories[category] = 1;
        }
      });

      const categoryChartData = Object.keys(categories).map((category, index) => ({
        name: category,
        value: categories[category],
        color: COLORS[index % COLORS.length]
      }));
      setCategoryData(categoryChartData);

      // Generate mock monthly spending data (in a real app, this would come from actual transaction data)
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
      const mockMonthlyData = months.map(month => {
        const record = { month };
        
        // For each category, generate some random spending amount
        Object.keys(categories).forEach(category => {
          // Random spending between $1000 and $10000
          record[category] = Math.floor(Math.random() * 9000) + 1000;
        });
        
        return record;
      });
      
      setMonthlyData(mockMonthlyData);
    }
  }, [vendors]);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip" style={{ 
          backgroundColor: '#fff', 
          padding: '10px', 
          border: '1px solid #ccc',
          borderRadius: '5px'
        }}>
          <p className="label" style={{ margin: 0 }}>{`${label}: ${payload[0].value}`}</p>
        </div>
      );
    }
    return null;
  };

  const calculateTotalSpending = () => {
    if (!monthlyData.length) return 0;
    
    let total = 0;
    monthlyData.forEach(month => {
      Object.keys(month).forEach(key => {
        if (key !== 'month') {
          total += month[key];
        }
      });
    });
    
    return total.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
  };

  const findTopVendorCategory = () => {
    if (!categoryData.length) return 'N/A';
    
    const sorted = [...categoryData].sort((a, b) => b.value - a.value);
    return sorted[0].name;
  };

  return (
    <div className="analytics-container">
      <h2>Vendor Analytics</h2>
      
      <div className="stats-cards">
        <div className="stat-card">
          <h4>Total Vendors</h4>
          <p className="stat-value">{vendors.length}</p>
        </div>
        <div className="stat-card">
          <h4>Total Categories</h4>
          <p className="stat-value">{categoryData.length}</p>
        </div>
        <div className="stat-card">
          <h4>Estimated Spending</h4>
          <p className="stat-value">{calculateTotalSpending()}</p>
        </div>
        <div className="stat-card">
          <h4>Top Category</h4>
          <p className="stat-value">{findTopVendorCategory()}</p>
        </div>
      </div>
      
      <div className="charts-container">
        <div className="chart-card">
          <h4>Vendor Categories Distribution</h4>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  labelLine={true}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  nameKey="name"
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="chart-card">
          <h4>Monthly Spending by Category</h4>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={monthlyData}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                {categoryData.map((category, index) => (
                  <Bar 
                    key={`bar-${index}`}
                    dataKey={category.name} 
                    stackId="a" 
                    fill={category.color} 
                  />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VendorAnalytics;