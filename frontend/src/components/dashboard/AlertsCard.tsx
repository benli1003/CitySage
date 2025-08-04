import { AlertTriangle } from "lucide-react";
import { DashboardCard } from "./DashboardCard";

interface Alert {
  id: string;
  type: 'warning' | 'info' | 'error';
  message: string;
}

const mockAlerts: Alert[] = [
  {
    id: "1",
    type: "warning",
    message: "Strong winds expected this afternoon"
  }
];

export const AlertsCard = () => {
  return (
    <DashboardCard
      title="Weather Alerts"
      icon={<AlertTriangle className="w-5 h-5" />}
    >
      <div className="space-y-3">
        {mockAlerts.map((alert) => (
          <div key={alert.id} className="flex items-start gap-3 p-3 bg-warning-muted rounded-lg border border-warning/20">
            <AlertTriangle className="w-5 h-5 text-warning mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-card-foreground">{alert.message}</p>
            </div>
          </div>
        ))}
      </div>
    </DashboardCard>
  );
};