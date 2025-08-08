import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_KEY = import.meta.env.VITE_WEATHER_API_KEY;

interface WeatherData {
  location: {
    name: string;
    region: string;
  };
  current: {
    temp_f: number;
    condition: {
      text: string;
      icon: string;
    };
    wind_mph: number;
  };
  forecast: {
    forecastday: Array<{
      day: {
        maxtemp_f: number;
        mintemp_f: number;
      };
    }>;
  };
}

export const WeatherCard = () => {
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    axios
      .get<WeatherData>('https://api.weatherapi.com/v1/forecast.json', {
        params: {
          key: API_KEY,
          q: 'Washington, DC',
          days: 1,
          aqi: 'no',
          alerts: 'no',
        },
      })
      .then((res) => {
        console.log('Weather API response:', res.data);
        setWeather(res.data);
      })
      .catch((err) => {
        console.error('Weather API error:', err.response || err.message);
        setError('Failed to fetch weather');
      });
  }, []);

  if (error) return (
    <div className="bg-card rounded-lg border border-border p-4">
      <h2 className="text-xl font-bold text-card-foreground mb-2">Weather</h2>
      <p className="text-destructive">{error}</p>
    </div>
  );
  if (!weather) return (
    <div className="bg-card rounded-lg border border-border p-4">
      <h2 className="text-xl font-bold text-card-foreground mb-2">Weather</h2>
      <p className="text-muted-foreground">Loading weather...</p>
    </div>
  );

  const today = weather.forecast.forecastday[0].day;

  return (
    <div className="bg-card rounded-lg border border-border p-4">
      <h2 className="text-xl font-bold text-card-foreground mb-2">Weather</h2>

      <p className="text-card-foreground">
        {weather.location.name}, {weather.location.region}
      </p>

      <div className="flex items-center my-2">
        <img
          src={`https:${weather.current.condition.icon}`}
          alt={weather.current.condition.text}
          className="w-6 h-6 mr-2"
        />
        <p className="text-muted-foreground">{weather.current.condition.text}</p>
      </div>

      <div className="flex items-baseline space-x-4">
        <p className="text-3xl font-bold text-card-foreground">
          {Math.round(weather.current.temp_f)}°F
        </p>
        <p className="text-sm text-muted-foreground">
          Wind: {weather.current.wind_mph} mph
        </p>
      </div>

      <div className="mt-2 flex space-x-4 text-sm text-muted-foreground">
        <p>High: {Math.round(today.maxtemp_f)}°</p>
        <p>Low: {Math.round(today.mintemp_f)}°</p>
      </div>
    </div>
  );
};
