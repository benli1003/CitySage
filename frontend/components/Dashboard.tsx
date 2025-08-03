import React from 'react'
import WmataBusFeed  from './WmataBusFeed'
import WmataRailFeed from './WmataRailFeed'
import TrafficSummary from './TrafficSummary'
import WeatherFeed from './WeatherFeed';

const Dashboard: React.FC = () => {
  return (
    <div className="dashboard-container p-6 bg-gray-100">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        CitySage Dashboard
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* traffic summaries*/}
        <div className="lg:col-span-2 space-y-6">
          {/* last hour */}
          <TrafficSummary hours = {1} title = "Traffic in the Last Hour" />

          {/* last 24 hours */}
          <TrafficSummary hours = {24} title = "Traffic in the Last 24 Hours" />
        </div>

        <div className="lg:col-span-1">
          <WeatherFeed />
        </div>

        {/* wmata alerts*/}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="p-4 border-b bg-blue-50">
            <h2 className="text-xl font-bold text-blue-700">Transit Alerts</h2>
            <p className="text-sm text-blue-500">
              Washington Metro Area Transit Authority
            </p>
          </div>
          <div className="p-4 max-h-[600px] overflow-y-auto">
            <WmataRailFeed />
            <WmataBusFeed />
          </div>
        </div>

      </div>
    </div>
  )
}

export default Dashboard
