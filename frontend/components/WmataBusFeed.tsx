import React, { useEffect, useState } from "react";

interface Alert {
  title: string;
  summary: string;
  time: string;
}

const WmataBusFeed: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        console.log("Fetching from: http://localhost:5050/api/alerts/bus");

        const res = await fetch("http://localhost:5050/api/alerts/bus", {
          method: "GET",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
        });

        console.log("Response status:", res.status);

        if (!res.ok) {
          const errorText = await res.text();
          console.error("Error response:", errorText);
          throw new Error(`Failed to fetch WMATA alerts: ${res.status} ${res.statusText}`);
        }

        const data = await res.json();
        console.log("Received data:", data);
        setAlerts(data.alerts || []);
      } catch (err: any) {
        console.error("Fetch error details:", err);
        setError(err.message);
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
