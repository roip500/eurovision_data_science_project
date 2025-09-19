import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { Music, BarChart3, Search, BookOpen, Target } from "lucide-react";

const Navigation = () => {
  const location = useLocation();
  
  const navItems = [
    { href: "/", label: "Home", icon: Music },
    { href: "/predict", label: "Predict", icon: Target },
    { href: "/visualizations", label: "Visualizations", icon: BarChart3 },
    { href: "/leaderboard", label: "Leaderboard", icon: Search },
    { href: "/about", label: "About", icon: BookOpen },
  ];

  return (
    <nav className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <Link to="/" className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
              <Music className="h-4 w-4 text-white" />
            </div>
            <span className="font-semibold text-lg">Eurovision Predictor</span>
          </Link>
          
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.href}
                  to={item.href}
                  className={cn(
                    "flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;