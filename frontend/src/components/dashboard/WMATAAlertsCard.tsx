import React, { useEffect, useState, useMemo } from "react";
import { Train, Bus, Filter } from "lucide-react";
import { DashboardCard } from "./DashboardCard";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
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
      return "bg-destructive/10 border-destructive/20 text-destructive dark:bg-destructive/20 dark:border-destructive/30 dark:text-destructive-foreground";
    case "major":
      return "bg-warning/10 border-warning/20 text-warning dark:bg-warning/20 dark:border-warning/30 dark:text-warning-foreground";
    default:
      return "bg-muted/50 border-border text-muted-foreground dark:bg-muted/30 dark:border-muted dark:text-muted-foreground";
  }
};

export const WMATAAlertsCard: React.FC = () => {
  const [alerts, setAlerts] = useState<WMATAAlert[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [severityFilter, setSeverityFilter] = useState<string>("all");
  const [dateFilter, setDateFilter] = useState<string>("today");
  const [showFilters, setShowFilters] = useState(false);

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

  const filteredAlerts = useMemo(() => {
    const filtered = alerts.filter((alert) => {
      if (severityFilter !== "all" && alert.severity !== severityFilter) {
        return false;
      }

      if (dateFilter !== "all") {
        const alertDate = new Date(alert.time);
        const now = new Date();
        
        switch (dateFilter) {
          case "today":
            return alertDate.toDateString() === now.toDateString();
          case "week": {
            const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
            return alertDate >= weekAgo;
          }
          case "month": {
            const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
            return alertDate >= monthAgo;
          }
          default:
            return true;
        }
      }

      return true;
    });

    return filtered.sort((a, b) => {
      const dateA = new Date(a.time);
      const dateB = new Date(b.time);
      return dateB.getTime() - dateA.getTime();
    });
  }, [alerts, severityFilter, dateFilter]);

  const resetFilters = () => {
    setSeverityFilter("all");
    setDateFilter("today");
  };

  const hasActiveFilters = severityFilter !== "all" || dateFilter !== "today";

  return (
    <DashboardCard title="WMATA Alerts" icon={<Train className="w-5 h-5" />}>
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
            className="gap-2"
          >
            <Filter className="w-4 h-4" />
            Filters
            {hasActiveFilters && (
              <span className="ml-1 px-1 py-0.5 text-xs bg-primary text-primary-foreground rounded">
                {[severityFilter !== "all" ? 1 : 0, dateFilter !== "all" ? 1 : 0].reduce((a, b) => a + b, 0)}
              </span>
            )}
          </Button>
          {hasActiveFilters && (
            <Button variant="ghost" size="sm" onClick={resetFilters}>
              Clear
            </Button>
          )}
        </div>

        {showFilters && (
          <div className="flex flex-col sm:flex-row gap-2 p-3 bg-muted/30 rounded-lg">
            <Select value={severityFilter} onValueChange={setSeverityFilter}>
              <SelectTrigger className="w-full sm:w-32">
                <SelectValue placeholder="Severity" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Severity</SelectItem>
                <SelectItem value="critical">Critical</SelectItem>
                <SelectItem value="major">Major</SelectItem>
                <SelectItem value="minor">Minor</SelectItem>
              </SelectContent>
            </Select>

            <Select value={dateFilter} onValueChange={setDateFilter}>
              <SelectTrigger className="w-full sm:w-32">
                <SelectValue placeholder="Date" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Time</SelectItem>
                <SelectItem value="today">Today</SelectItem>
                <SelectItem value="week">Past Week</SelectItem>
                <SelectItem value="month">Past Month</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )}

        {error && <p className="text-destructive">{error}</p>}
        {!error && filteredAlerts.length === 0 && alerts.length > 0 && (
          <p className="text-sm text-muted-foreground">No alerts match the current filters</p>
        )}
        {!error && alerts.length === 0 && (
          <p className="text-sm text-muted-foreground">No current alerts</p>
        )}
        {filteredAlerts.map((alert) => (
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
