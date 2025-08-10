import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface LandingPageProps {
  onAnimationComplete: () => void;
}

export const LandingPage = ({ onAnimationComplete }: LandingPageProps) => {
  const [showLanding, setShowLanding] = useState(true);
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowLanding(false);
      setTimeout(onAnimationComplete, 1000);
    }, 2500);

    return () => clearTimeout(timer);
  }, [onAnimationComplete]);

  return (
    <AnimatePresence>
      {showLanding && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ 
            scale: 0.8,
            opacity: 0,
            y: -50,
            transition: { 
              duration: 1,
              ease: [0.25, 0.1, 0.25, 1]
            }
          }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-br from-background via-background to-muted/20"
        >
          <div className="text-center space-y-8">
            <motion.div
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ 
                duration: 0.8,
                delay: 0.2,
                ease: [0.25, 0.1, 0.25, 1]
              }}
              className="relative"
            >
              <h1 className="text-8xl md:text-9xl font-bold bg-gradient-to-r from-primary via-primary/80 to-primary/60 bg-clip-text text-transparent">
                CitySage
              </h1>
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: "100%" }}
                transition={{ 
                  duration: 1.2,
                  delay: 1,
                  ease: [0.25, 0.1, 0.25, 1]
                }}
                className="absolute -bottom-4 left-0 h-1 bg-gradient-to-r from-primary via-primary/60 to-transparent"
              />
            </motion.div>
            
            <motion.p
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ 
                duration: 0.6,
                delay: 0.8,
                ease: [0.25, 0.1, 0.25, 1]
              }}
              className="text-xl md:text-2xl text-muted-foreground font-light tracking-wide"
            >
              Urban Intelligence Dashboard
            </motion.p>

            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ 
                duration: 0.4,
                delay: 1.2,
                ease: [0.25, 0.1, 0.25, 1]
              }}
              className="flex items-center justify-center space-x-2 text-primary/60"
            >
              <div className="w-2 h-2 bg-primary/40 rounded-full animate-pulse" />
              <div className="w-2 h-2 bg-primary/60 rounded-full animate-pulse [animation-delay:0.2s]" />
              <div className="w-2 h-2 bg-primary/80 rounded-full animate-pulse [animation-delay:0.4s]" />
            </motion.div>
          </div>

          <div className="absolute inset-0 opacity-[0.02]">
            <div className="absolute top-10 left-10 w-32 h-32 bg-primary rounded-full blur-3xl" />
            <div className="absolute bottom-10 right-10 w-48 h-48 bg-primary/50 rounded-full blur-3xl" />
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-primary/30 rounded-full blur-3xl" />
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};