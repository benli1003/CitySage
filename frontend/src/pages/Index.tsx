import { useState } from "react";
import { Dashboard } from "@/components/dashboard/Dashboard";
import { LandingPage } from "@/components/LandingPage";

const Index = () => {
  const [showLanding, setShowLanding] = useState(true);

  const handleAnimationComplete = () => {
    setShowLanding(false);
  };

  return (
    <>
      {showLanding && <LandingPage onAnimationComplete={handleAnimationComplete} />}
      <Dashboard />
    </>
  );
};

export default Index;
