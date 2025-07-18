import React from 'react';
import WmataBusFeed from './WmataBusFeed';
import WmataRailFeed from './WmataRailFeed';

const Dashboard: React.FC = () => {
  return (
    <div className="dashboard-container p-6 bg-gray-100">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">CitySage Dashboard</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Traffic Camera Section - Takes 2/3 of width on larger screens */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow-md overflow-hidden">
          <div className="p-4 border-b">
            <h2 className="text-xl font-bold text-gray-700">Traffic Monitoring</h2>
            <p className="text-sm text-gray-500">I-295 South near I-495</p>
          </div>
          <div className="relative" style={{ paddingBottom: "56.25%" }}>
            <iframe 
              src="http://localhost:5000/video" 
              className="absolute top-0 left-0 w-full h-full border-0"
              title="Live Traffic Feed"
              allowFullScreen
            ></iframe>
          </div>
          <div className="p-4 bg-gray-50">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
              <span className="text-sm font-medium">Live Feed</span>
            </div>
          </div>
        </div>
        
        {/* WMATA Alerts Section - Takes 1/3 of width */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="p-4 border-b bg-blue-50">
            <h2 className="text-xl font-bold text-blue-700">Transit Alerts</h2>
            <p className="text-sm text-blue-500">Washington Metro Area Transit Authority</p>
          </div>
          <div className="p-4 max-h-[600px] overflow-y-auto">
            <WmataRailFeed />
            <WmataBusFeed />
          </div>
        </div>
      </div>      
    </div>
  );
};

export default Dashboard;
