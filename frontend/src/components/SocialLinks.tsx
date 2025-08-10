import { Github, Linkedin, Share2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

const socialLinks = [
  {
    name: "LinkedIn",
    url: "https://www.linkedin.com/in/benjaminliumd/",
    icon: Linkedin,
    color: "text-blue-600 hover:text-blue-700"
  },
  {
    name: "GitHub", 
    url: "https://github.com/benli1003",
    icon: Github,
    color: "text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
  }
];

export function SocialLinks() {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          <Share2 className="h-4 w-4" />
          <span className="hidden sm:inline">Connect</span>
          <span className="sr-only">Social links</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-48 p-3 bg-background border border-border shadow-md" align="end">
        <div className="space-y-2">
          <p className="text-xs font-medium text-muted-foreground mb-3">Connect with me</p>
          {socialLinks.map((social) => (
            <a
              key={social.name}
              href={social.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 p-2 rounded-md hover:bg-accent transition-colors group"
            >
              <social.icon className={`h-4 w-4 ${social.color} transition-colors`} />
              <span className="text-sm font-medium group-hover:text-accent-foreground">
                {social.name}
              </span>
            </a>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
}