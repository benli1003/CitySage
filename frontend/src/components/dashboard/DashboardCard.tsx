import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface DashboardCardProps {
  title: string;
  icon?: ReactNode;
  children: ReactNode;
  className?: string;
  fullWidth?: boolean;
}

export const DashboardCard = ({ title, icon, children, className, fullWidth }: DashboardCardProps) => {
  return (
    <div 
      className={cn(
        "bg-card border border-card-border rounded-lg p-6 transition-all duration-200",
        "hover:shadow-[var(--shadow-card-hover)] shadow-[var(--shadow-card)]",
        fullWidth && "col-span-full",
        className
      )}
    >
      <div className="flex items-center gap-3 mb-4">
        {icon && (
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary/10 text-primary">
            {icon}
          </div>
        )}
        <h2 className="text-lg font-semibold text-card-foreground">{title}</h2>
      </div>
      <div>{children}</div>
    </div>
  );
};