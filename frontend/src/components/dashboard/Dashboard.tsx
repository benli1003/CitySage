import { WeatherCard } from "./WeatherCard";
import { TrafficCard } from "./TrafficCard";
import { WMATAAlertsCard } from "./WMATAAlertsCard";
import { AISummaryCard } from "./AISummaryCard";
import { ThemeToggle } from "@/components/theme-toggle";

export const Dashboard = () => {
  return (
    <div className="min-h-screen bg-background">
      <header className="bg-card border-b border-border px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold text-foreground">CitySage Dashboard</h1>
          <ThemeToggle />
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-6">
            <WeatherCard />
            <WMATAAlertsCard />
          </div>
          
          <div className="md:col-span-2">
            <TrafficCard />
          </div>
        </div>
      </main>
    </div>
  );
};