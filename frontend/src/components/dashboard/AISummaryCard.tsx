import { Bot, RefreshCw } from "lucide-react";
import { DashboardCard } from "./DashboardCard";
import { Button } from "@/components/ui/button";

export const AISummaryCard = () => {
  return (
    <DashboardCard
      title="AI Summary"
      icon={<Bot className="w-5 h-5" />}
      fullWidth
    >
      <div className="space-y-4">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
            <Bot className="w-5 h-5 text-primary" />
          </div>
          <div className="flex-1">
            <p className="text-sm text-card-foreground leading-relaxed">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor 
              incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud 
              exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
            </p>
          </div>
        </div>
        
        <div className="flex justify-end pt-2 border-t border-border">
          <Button variant="outline" size="sm" className="gap-2">
            <RefreshCw className="w-4 h-4" />
            Refresh Summary
          </Button>
        </div>
      </div>
    </DashboardCard>
  );
};