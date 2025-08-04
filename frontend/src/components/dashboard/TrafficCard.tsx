import { Navigation, Brain } from "lucide-react";
import { DashboardCard } from "./DashboardCard";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { useState } from "react";

const cameraFeeds = [
  { id: "i495-inner", name: "I-495 Inner Loop at Tysons" },
  { id: "i66-eastbound", name: "I-66 Eastbound at Fairfax" },
  { id: "i270-south", name: "I-270 Southbound at Rockville" },
  { id: "gwb-south", name: "GW Parkway Southbound at Key Bridge" },
  { id: "395-north", name: "I-395 Northbound at Pentagon" }
];

export const TrafficCard = () => {
  const [selectedCamera, setSelectedCamera] = useState(cameraFeeds[0].id);

  return (
    <DashboardCard
      title="Live Traffic Feed"
      icon={<Navigation className="w-5 h-5" />}
    >
      <div className="space-y-3">
        {/* Camera Feed Selector */}
        <Select value={selectedCamera} onValueChange={setSelectedCamera}>
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select camera feed" />
          </SelectTrigger>
          <SelectContent>
            {cameraFeeds.map((feed) => (
              <SelectItem key={feed.id} value={feed.id}>
                {feed.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* Traffic Feed Display */}
        <div className="w-full h-48 bg-success/10 rounded-lg border border-success/20 relative overflow-hidden">
          {/* Simple traffic visualization */}
          <div className="absolute inset-0 flex items-center justify-center">
            <svg className="w-full h-full" viewBox="0 0 200 150">
              {/* Traffic lines */}
              <path d="M20 30 Q100 75 180 30" stroke="hsl(var(--success))" strokeWidth="3" fill="none" opacity="0.8" />
              <path d="M20 60 Q100 105 180 60" stroke="hsl(var(--warning))" strokeWidth="3" fill="none" opacity="0.8" />
              <path d="M20 90 Q100 45 180 90" stroke="hsl(var(--destructive))" strokeWidth="3" fill="none" opacity="0.8" />
              <path d="M20 120 Q100 15 180 120" stroke="hsl(var(--primary))" strokeWidth="3" fill="none" opacity="0.8" />
            </svg>
          </div>
        </div>
        <div className="text-sm text-muted-foreground">
          {cameraFeeds.find(feed => feed.id === selectedCamera)?.name}
        </div>

        {/* AI Traffic Summary Section */}
        <div className="pt-4 border-t border-border">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Brain className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium text-card-foreground">AI Traffic Summary</span>
            </div>
            <Button variant="outline" size="sm">
              Refresh
            </Button>
          </div>
          <div className="bg-muted/50 rounded-lg p-4">
            <p className="text-sm text-card-foreground leading-relaxed">
              Current traffic conditions show moderate congestion on I-495 Inner Loop with 15-minute delays. 
              I-66 Eastbound is experiencing heavy traffic due to ongoing construction. Alternative routes via 
              I-270 are recommended for faster travel times. Expected clear-up by 7:30 PM.
            </p>
            <div className="mt-3 flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-success"></div>
                <span className="text-xs text-muted-foreground">Light Traffic</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-warning"></div>
                <span className="text-xs text-muted-foreground">Moderate Traffic</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-destructive"></div>
                <span className="text-xs text-muted-foreground">Heavy Traffic</span>
              </div>
            </div>
          </div>
        </div>

        {/* 24 Hour Traffic Summary */}
        <div className="pt-4 border-t border-border">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-card-foreground">Last 24 Hours</span>
          </div>
          <div className="bg-muted/30 rounded-lg p-4">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-lg font-semibold text-card-foreground">12</div>
                <div className="text-xs text-muted-foreground">Peak Hours</div>
              </div>
              <div>
                <div className="text-lg font-semibold text-card-foreground">35min</div>
                <div className="text-xs text-muted-foreground">Avg Delay</div>
              </div>
              <div>
                <div className="text-lg font-semibold text-card-foreground">8</div>
                <div className="text-xs text-muted-foreground">Incidents</div>
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-border">
              <p className="text-xs text-muted-foreground">
                Heaviest traffic between 7-9 AM and 5-7 PM. Construction on I-66 caused 20min delays.
              </p>
            </div>
          </div>
        </div>
      </div>
    </DashboardCard>
  );
};