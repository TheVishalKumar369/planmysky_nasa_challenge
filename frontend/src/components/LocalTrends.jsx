import React from "react";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

// Dummy data for overall trends
const activityData = [
  { name: "Going Outside", value: 65 },
  { name: "Staying Home", value: 35 },
];

// Dummy data for user reports
const reports = [
  { id: 1, city: "Kathmandu", issue: "Flood" },
  { id: 3, city: "Islamabad", issue: "Heavy Rain" },
  { id: 4, city: "Quetta", issue: "Strong Winds" },
];

const COLORS = ["#82ca9d", "#8884d8", "#ff7f50"];

const LocalTrends = () => {
  return (
    <div className="local-trends">
      <h3>📊 Local Trends & Stats</h3>
      <p>Community activity overview</p>

      {/* Activity Pie Chart */}
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={activityData}
              dataKey="value"
              nameKey="name"
              outerRadius={100}
              fill="#8884d8"
            >
              {activityData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Reports Section */}
      <div className="reports-section">
        <h4>🚨 Reports from Community</h4>
        <ul className="reports-list">
          {reports.map((report) => (
            <li key={report.id}>
              <strong>{report.city}:</strong> {report.issue}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default LocalTrends;
