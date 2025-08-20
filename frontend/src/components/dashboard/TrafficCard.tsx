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
import { Skeleton } from "@/components/ui/skeleton";
import { useState, useEffect } from "react";
import axios from "axios";

const cameraFeeds = [
  { id: "i95-north-of-i495", name: "I-95 Northbound just north of I-495" },
  { id: "i495-east-of-i270", name: "I-495 Eastbound just east of I-270" },
  { id: "i495-american-legion-bridge", name: "I-495 American Legion Bridge" },
  { id: "i495-connecticut-ave", name: "I-495 at Connecticut Avenue" },
  { id: "i495-georgia-ave", name: "I-495 at Georgia Avenue" },
  { id: "i495-new-hampshire-ave", name: "I-495 at New Hampshire Avenue" },
  { id: "i495-colesville-rd", name: "I-495 at Colesville Road" },
  { id: "i495-university-blvd", name: "I-495 at University Boulevard" },
  { id: "i270-rockville-pike", name: "I-270 at Rockville Pike" },
  { id: "i270-montrose-rd", name: "I-270 at Montrose Road" },
  { id: "i270-old-georgetown-rd", name: "I-270 at Old Georgetown Road" }
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
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 sm:gap-2 mb-4">
        <Select value={hours.toString()} onValueChange={(v) => setHours(Number(v))}>
          <SelectTrigger className="w-full sm:w-24 min-h-[44px] sm:min-h-[36px]">
            <SelectValue placeholder="Hours" />
          </SelectTrigger>
          <SelectContent>
            {hoursOptions.map((h) => (
              <SelectItem key={h} value={h.toString()} className="min-h-[44px] sm:min-h-[36px]">
                Last {h}h
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={camera}
          onValueChange={(val) => setCamera(val)}
        >
          <SelectTrigger className="w-full sm:w-48 min-h-[44px] sm:min-h-[36px]">
            <SelectValue placeholder="All Cameras" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all" className="min-h-[44px] sm:min-h-[36px]">All Cameras</SelectItem>
            {cameraFeeds.map((feed) => (
              <SelectItem key={feed.id} value={feed.id} className="min-h-[44px] sm:min-h-[36px]">
                {feed.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Button size="sm" onClick={() => fetchSummary(hours, camera, setLiveSummary, setLoadingLive, setErrorLive)} disabled={loadingLive} className="min-h-[44px] sm:min-h-[36px] w-full sm:w-auto">
          {loadingLive ? "Loading…" : "Refresh"}
        </Button>
      </div>

      <div className="mb-6">
        <TrafficFootageCard />
      </div>

      {errorLive && <div className="text-destructive text-sm mb-2">{errorLive}</div>}
      <div className="bg-muted/50 rounded-lg p-4 mb-8 transition-all duration-200 hover:bg-muted/60 hover:shadow-sm cursor-pointer">
        <div className="flex items-center mb-2">
          <Brain className="w-4 h-4 text-primary mr-1" />
          <span className="text-sm font-medium">AI Traffic Summary</span>
        </div>
        {loadingLive ? (
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-4/5" />
          </div>
        ) : (
          <p className="text-sm leading-relaxed">
            {liveSummary || "No data available for that selection."}
          </p>
        )}
      </div>

      <div>
        <h3 className="text-sm font-medium mb-2">Last 24 Hours</h3>
        <div className="bg-muted/30 rounded-lg p-4 transition-all duration-200 hover:bg-muted/40 hover:shadow-sm cursor-pointer">
          {loading24 ? (
            <div className="space-y-2">
              <Skeleton className="h-3 w-full" />
              <Skeleton className="h-3 w-4/5" />
              <Skeleton className="h-3 w-3/4" />
            </div>
          ) : (
            <p className="text-xs text-muted-foreground leading-relaxed">
              {summary24}
            </p>
          )}
        </div>
      </div>
    </DashboardCard>
  );
};
