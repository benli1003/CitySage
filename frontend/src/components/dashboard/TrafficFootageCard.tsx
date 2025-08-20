import { Video, AlertCircle } from "lucide-react";
import { DashboardCard } from "./DashboardCard";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { useState, useRef, useEffect } from "react";
import Hls from "hls.js";
import axios from "axios";

interface Camera {
  id: string;
  name: string;
  logging_url: string;
  streaming_url: string;
}

export const TrafficFootageCard = () => {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [loadingCameras, setLoadingCameras] = useState(true);
  const videoRef = useRef<HTMLVideoElement>(null);
  const hlsRef = useRef<Hls | null>(null);

  useEffect(() => {
    const fetchCameras = async () => {
      try {
        const response = await axios.get("/api/cameras");
        const cameraList = response.data.cameras;
        setCameras(cameraList);
        if (cameraList.length > 0) {
          setSelectedCamera(cameraList[0].id);
        }
      } catch (error) {
        console.error("Failed to fetch camera configurations:", error);
        setHasError(true);
      } finally {
        setLoadingCameras(false);
      }
    };

    fetchCameras();
  }, []);

  useEffect(() => {
    const video = videoRef.current;
    const selectedCameraObj = cameras.find(cam => cam.id === selectedCamera);
    const streamUrl = selectedCameraObj?.streaming_url;
    
    if (!video || !streamUrl) return;

    setIsLoading(true);
    setHasError(false);

    const handleCanPlay = () => {
      setIsLoading(false);
      setHasError(false);
    };

    const handleError = () => {
      setIsLoading(false);
      setHasError(true);
    };

    const handleLoadedData = () => {
      setIsLoading(false);
      setHasError(false);
    };

    video.addEventListener('canplay', handleCanPlay);
    video.addEventListener('error', handleError);
    video.addEventListener('loadeddata', handleLoadedData);

    if (hlsRef.current) {
      hlsRef.current.destroy();
      hlsRef.current = null;
    }

    if (Hls.isSupported()) {
      const hls = new Hls({
        enableWorker: false,
        lowLatencyMode: true,
        backBufferLength: 90,
      });
      
      hlsRef.current = hls;
      
      hls.on(Hls.Events.ERROR, (event, data) => {
        console.error('HLS error:', data);
        if (data.fatal) {
          setHasError(true);
          setIsLoading(false);
        }
      });

      hls.on(Hls.Events.FRAG_LOADED, () => {
        setIsLoading(false);
      });

      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        video.play().catch(() => {
        });
      });

      hls.loadSource(streamUrl);
      hls.attachMedia(video);
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = streamUrl;
      video.addEventListener('loadedmetadata', () => {
        video.play().catch(() => {
        });
      });
    } else {
      setHasError(true);
      setIsLoading(false);
      console.error('HLS not supported in this browser');
    }

    return () => {
      video.removeEventListener('canplay', handleCanPlay);
      video.removeEventListener('error', handleError);
      video.removeEventListener('loadeddata', handleLoadedData);
      
      if (hlsRef.current) {
        hlsRef.current.destroy();
        hlsRef.current = null;
      }
    };
  }, [selectedCamera, cameras]);

  if (loadingCameras) {
    return (
      <DashboardCard
        title="Live Traffic Footage"
        icon={<Video className="w-5 h-5" />}
        fullWidth
      >
        <div className="space-y-4">
          <Skeleton className="h-10 w-full" />
          <div className="relative w-full aspect-video bg-muted/30 rounded-lg overflow-hidden">
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="flex flex-col items-center gap-2">
                <Skeleton className="w-8 h-8 rounded-full" />
                <Skeleton className="h-4 w-32" />
              </div>
            </div>
          </div>
          <div className="space-y-1">
            <Skeleton className="h-3 w-48" />
            <Skeleton className="h-3 w-56" />
            <Skeleton className="h-3 w-64" />
          </div>
        </div>
      </DashboardCard>
    );
  }

  return (
    <DashboardCard
      title="Live Traffic Footage"
      icon={<Video className="w-5 h-5" />}
      fullWidth
    >
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Select
            value={selectedCamera}
            onValueChange={setSelectedCamera}
            disabled={cameras.length === 0}
          >
            <SelectTrigger className="w-full min-h-[44px] sm:min-h-[40px]">
              <SelectValue placeholder="Select camera" />
            </SelectTrigger>
            <SelectContent>
              {cameras.map((camera) => (
                <SelectItem key={camera.id} value={camera.id} className="min-h-[44px] sm:min-h-[36px]">
                  {camera.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="relative w-full aspect-video bg-muted/30 rounded-lg overflow-hidden">
          {hasError ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-muted-foreground">
              <AlertCircle className="w-8 h-8 mb-2" />
              <p className="text-sm">Unable to load video stream</p>
              <p className="text-xs">The camera feed may be temporarily unavailable</p>
            </div>
          ) : (
            <>
              {isLoading && (
                <div className="absolute inset-0 flex items-center justify-center bg-muted/50 z-10">
                  <div className="flex flex-col items-center gap-2">
                    <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                    <p className="text-sm text-muted-foreground">Loading video stream...</p>
                  </div>
                </div>
              )}
              <video
                ref={videoRef}
                className="w-full h-full object-cover"
                autoPlay
                muted
                playsInline
                controls
                preload="metadata"
              >
                Your browser does not support the video tag.
              </video>
            </>
          )}
        </div>

        <div className="text-xs text-muted-foreground">
          <p>Live feed from {cameras.find(c => c.id === selectedCamera)?.name}</p>
          <p>Stream may have a 15-30 second delay</p>
        </div>
        <div className="mt-2 p-2 bg-amber-100 border border-amber-300 rounded-lg dark:bg-amber-950 dark:border-amber-800">
          <p className="text-xs font-medium text-amber-800 dark:text-amber-300">Wait a few seconds between camera switches to prevent buffering issues!</p>
        </div>
      </div>
    </DashboardCard>
  );
};