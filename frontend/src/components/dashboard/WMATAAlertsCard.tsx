import React, { useEffect, useState } from "react";
import { Train, Bus } from "lucide-react";
import { DashboardCard } from "./DashboardCard";
import axios from "axios";

interface WMATAAlert {
  id: string;
  type: "bus" | "rail";
  title: string;
  summary: string;
  time: string;
  severity?: "minor" | "major" | "critical";
}

const getSeverityColor = (severity: string | undefined) => {
  switch (severity) {
    case "critical":
      return "bg-destructive-muted border-destructive/20 text-destructive-foreground";
    case "major":
      return "bg-warning-muted border-warning/20 text-warning-foreground";
    default:
      return "bg-muted border-border text-muted-foreground";
  }
};

export const WMATAAlertsCard: React.FC = () => {
  const [alerts, setAlerts] = useState<WMATAAlert[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const railPromise = axios.get<{ alerts?: WMATAAlert[] }>("/api/alerts/rail");
        const busPromise  = axios.get<{ alerts?: WMATAAlert[] }>("/api/alerts/bus");

        const [railRes, busRes] = await Promise.all([railPromise, busPromise]);

        const railAlerts = (railRes.data.alerts ?? []).map((a) => ({
          ...a,
          type: "rail" as const,
        }));
        const busAlerts = (busRes.data.alerts ?? []).map((a) => ({
          ...a,
          type: "bus" as const,
        }));

        setAlerts([...railAlerts, ...busAlerts]);
      } catch (err) {
        console.error("Error fetching WMATA alerts:", err);
        setError("Could not load WMATA alerts");
      }
    };

    fetchAlerts();
  }, []);

  return (
    <DashboardCard title="WMATA Alerts" icon={<Train className="w-5 h-5" />}>
      <div className="space-y-3">
        {error && <p className="text-red-600">{error}</p>}
        {!error && alerts.length === 0 && (
          <p className="text-sm text-muted-foreground">No current alerts</p>
        )}
        {alerts.map((alert) => (
          <div
            key={`${alert.type}-${alert.id}`}
            className={`flex items-start gap-3 p-3 rounded-lg border ${getSeverityColor(
              alert.severity
            )}`}
          >
            <div className="flex-shrink-0 mt-0.5">
              {alert.type === "rail" ? (
                <Train className="w-4 h-4" />
              ) : (
                <Bus className="w-4 h-4" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm font-medium">{alert.title}</span>
                <span className="text-xs opacity-70">{alert.time}</span>
              </div>
              <p className="text-sm leading-tight">{alert.summary}</p>
            </div>
          </div>
        ))}
      </div>
    </DashboardCard>
  );
};
