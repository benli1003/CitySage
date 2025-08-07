import { Navigation, Brain } from "lucide-react";
import { DashboardCard } from "./DashboardCard";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import axios from "axios";

const hoursOptions = [1, 3, 6, 12];

export const TrafficCard = () => {
  const [hours, setHours] = useState(1);
  const [liveSummary, setLiveSummary] = useState("");
  const [loadingLive, setLoadingLive] = useState(false);
  const [errorLive, setErrorLive] = useState<string | null>(null);

  const [summary24, setSummary24] = useState("");
  const [loading24, setLoading24] = useState(true);

  const fetchSummary = async (h: number, setter: (s: string) => void, setLoading: (b: boolean) => void) => {
    setLoading(true);
    try {
      const res = await axios.get("/api/traffic-summary", { params: { hours: h } });
      setter(res.data.summary);
    } catch {
      setter("Failed to load summary.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary(hours, setLiveSummary, setLoadingLive);
  }, [hours]);

  useEffect(() => {
    fetchSummary(24, setSummary24, setLoading24);
  }, []);

  return (
    <DashboardCard title="Live Traffic Feed" icon={<Navigation className="w-5 h-5" />}>
      <div className="flex items-center gap-2 mb-4">
        <Select value={hours.toString()} onValueChange={val => setHours(Number(val))}>
          <SelectTrigger className="w-24">
            <SelectValue placeholder="Hours" />
          </SelectTrigger>
          <SelectContent>
            {hoursOptions.map(h => (
              <SelectItem key={h} value={h.toString()}>
                Last {h}h
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button size="sm" onClick={() => fetchSummary(hours, setLiveSummary, setLoadingLive)} disabled={loadingLive}>
          {loadingLive ? "Refreshing…" : "Refresh"}
        </Button>
      </div>

      <div className="bg-muted/50 rounded-lg p-4 mb-8">
        <div className="flex items-center mb-2">
          <Brain className="w-4 h-4 text-primary mr-1" />
          <span className="text-sm font-medium">AI Traffic Summary</span>
        </div>
        <p className="text-sm leading-relaxed">
          {loadingLive ? "Loading…" : liveSummary || "No data available."}
        </p>
      </div>

      <div>
        <h3 className="text-sm font-medium mb-2">Last 24 Hours</h3>
        <div className="bg-muted/30 rounded-lg p-4">
          <p className="text-xs text-muted-foreground leading-relaxed">
            {loading24 ? "Loading…" : summary24}
          </p>
        </div>
      </div>
    </DashboardCard>
  );
};
