import { motion } from "framer-motion";
import { WeatherCard } from "./WeatherCard";
import { TrafficCard } from "./TrafficCard";
import { WMATAAlertsCard } from "./WMATAAlertsCard";
import { AISummaryCard } from "./AISummaryCard";
import { ThemeToggle } from "@/components/theme-toggle";
import { SocialLinks } from "@/components/SocialLinks";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.6,
      staggerChildren: 0.1,
      delayChildren: 0.3
    }
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: { duration: 0.5, ease: [0.25, 0.1, 0.25, 1] }
  }
};

export const Dashboard = () => {
  return (
    <motion.div 
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="min-h-screen bg-background"
    >
      <motion.header 
        variants={itemVariants}
        className="bg-card border-b border-border px-4 sm:px-6 py-4"
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <motion.h1 
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
            className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-primary to-primary/80 bg-clip-text text-transparent"
          >
            CitySage Dashboard
          </motion.h1>
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.6 }}
            className="flex items-center gap-2 sm:gap-3"
          >
            <SocialLinks />
            <ThemeToggle />
          </motion.div>
        </div>
      </motion.header>

      <motion.main 
        variants={itemVariants}
        className="max-w-7xl mx-auto p-4 sm:p-6"
      >
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
          <motion.div 
            variants={itemVariants}
            className="lg:col-span-2 lg:order-2 order-1"
          >
            <TrafficCard />
          </motion.div>
          
          <motion.div 
            variants={containerVariants}
            className="lg:order-1 order-2 space-y-4 sm:space-y-6"
          >
            <motion.div variants={itemVariants}>
              <WeatherCard />
            </motion.div>
            <motion.div variants={itemVariants}>
              <WMATAAlertsCard />
            </motion.div>
          </motion.div>
        </div>
      </motion.main>
    </motion.div>
  );
};