import { MessageCircle } from "lucide-react";
import { DashboardCard } from "./DashboardCard";

interface Tweet {
  id: string;
  text: string;
  timestamp: string;
}

const mockTweets: Tweet[] = [
  {
    id: "1",
    text: "Tweet text goes here",
    timestamp: "2h"
  },
  {
    id: "2", 
    text: "Tweet text goes here",
    timestamp: "1h"
  },
  {
    id: "3",
    text: "Tweet text goes here", 
    timestamp: "3h"
  }
];

export const TweetsCard = () => {
  return (
    <DashboardCard
      title="Trending Tweets"
      icon={<MessageCircle className="w-5 h-5" />}
    >
      <div className="space-y-3">
        {mockTweets.map((tweet) => (
          <div key={tweet.id} className="p-3 bg-muted/30 rounded-lg border border-border/50">
            <p className="text-sm text-card-foreground mb-2">{tweet.text}</p>
            <span className="text-xs text-muted-foreground">{tweet.timestamp}</span>
          </div>
        ))}
      </div>
    </DashboardCard>
  );
};