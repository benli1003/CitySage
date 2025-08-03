import React, { useEffect, useState } from "react";
import axios from "axios";

interface Alert {
  title: string;
  summary: string;
  time: string;
}

const WmataBusFeed: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        console.log("Fetching from: /api/alerts/bus");
        const res = await axios.get<{ alerts: Alert[] }>("/api/alerts/bus");
        console.log("Response data:", res.data);
        setAlerts(res.data.alerts || []);
      } catch (err: any) {
        console.error("Axios error details:", err);
        if (err.response) {
          setError(`Failed to fetch WMATA alerts: ${err.response.status} ${err.response.statusText}`);
        } else {
          setError(err.message);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchAlerts();
  }, []);

  return (
    <div>
      <h2 className="text-xl font-bold mt-4 mb-2">Bus Alerts</h2>

      {loading && <p>Loading WMATA alerts...</p>}
      {error && <p className="text-red-500">Error: {error}</p>}
      {!loading && !error && alerts.length === 0 && (
        <p>No WMATA alerts at the moment.</p>
      )}

      <ul className="space-y-4">
        {alerts.map((alert, idx) => (
          <li key={idx} className="border p-3 rounded shadow">
            <h3 className="font-semibold">{alert.title}</h3>
            <p className="text-sm text-gray-700">{alert.summary}</p>
            <p className="text-xs text-gray-500 italic">{alert.time}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default WmataBusFeed;
