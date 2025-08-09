import { Navigation, Brain } from "lucide-react";
import { DashboardCard } from "./DashboardCard";
import { TrafficFootageCard } from "./TrafficFootageCard";
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

const cameraFeeds = [
  { id: "i95-north-of-i495", name: "I-95 Northbound just north of I-495" },
  { id: "i495-east-of-i270", name: "I-495 Eastbound just east of I-270" }
];

const hoursOptions = [1, 3, 6, 12];

export const TrafficCard = () => {
  const [hours, setHours] = useState(1);
  const [camera, setCamera] = useState<"all" | string>("all");
  const [liveSummary, setLiveSummary] = useState("");
  const [loadingLive, setLoadingLive] = useState(false);
  const [errorLive, setErrorLive] = useState<string | null>(null);

  const [summary24, setSummary24] = useState("");
  const [loading24, setLoading24] = useState(true);

  const fetchSummary = async (
    h: number,
    cam: string,
    setSummary: (s: string) => void,
    setLoading: (b: boolean) => void,
    setError?: (e: string | null) => void
  ) => {
    setLoading(true);
    setError?.(null);

    try {
      const res = await axios.get("/api/traffic-summary", {
        params: {
          hours: h,
          ...(cam && cam !== "all" ? { camera_id: cam } : {}),
        },
      });
      setSummary(res.data.summary);
    } catch (e: unknown) {
      setSummary("Failed to load summary.");
      const error = e as { response?: { data?: { error?: string } }; message?: string };
      setError?.(error.response?.data?.error || error.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary(
      hours,
      camera,
      setLiveSummary,
      setLoadingLive,
      setErrorLive
    );
  }, [hours, camera]);

  useEffect(() => {
    fetchSummary(24, "all", setSummary24, setLoading24);
  }, []);

  return (
    <DashboardCard title="Live Traffic Feed" icon={<Navigation className="w-5 h-5" />}>
      <div className="flex items-center gap-2 mb-4">
        <Select value={hours.toString()} onValueChange={(v) => setHours(Number(v))}>
          <SelectTrigger className="w-24">
            <SelectValue placeholder="Hours" />
          </SelectTrigger>
          <SelectContent>
            {hoursOptions.map((h) => (
              <SelectItem key={h} value={h.toString()}>
                Last {h}h
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={camera}
          onValueChange={(val) => setCamera(val)}
        >
          <SelectTrigger className="w-48">
            <SelectValue placeholder="All Cameras" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Cameras</SelectItem>
            {cameraFeeds.map((feed) => (
              <SelectItem key={feed.id} value={feed.id}>
                {feed.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Button size="sm" onClick={() => fetchSummary(hours, camera, setLiveSummary, setLoadingLive, setErrorLive)} disabled={loadingLive}>
          {loadingLive ? "Loading…" : "Refresh"}
        </Button>
      </div>

      <div className="mb-6">
        <TrafficFootageCard />
      </div>

      {errorLive && <div className="text-destructive text-sm mb-2">{errorLive}</div>}
      <div className="bg-muted/50 rounded-lg p-4 mb-8">
        <div className="flex items-center mb-2">
          <Brain className="w-4 h-4 text-primary mr-1" />
          <span className="text-sm font-medium">AI Traffic Summary</span>
        </div>
        <p className="text-sm leading-relaxed">
          {loadingLive ? "Loading…" : liveSummary || "No data available for that selection."}
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
