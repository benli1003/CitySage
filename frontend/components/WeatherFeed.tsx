import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_KEY = import.meta.env.VITE_WEATHER_API_KEY;

const WeatherFeed = () => {
  const [weather, setWeather] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    axios
      .get('https://api.weatherapi.com/v1/current.json', {
        params: {
          key: API_KEY,
          q: 'Washington',
        },
      })
      .then((res) => {
        console.log("Weather API response:", res.data);
        setWeather(res.data);
      })
      .catch((err) => {
        console.error("Weather API error:", err.response || err.message);
        setError('Failed to fetch weather');
      });
  }, []);

  if (error) return <div>{error}</div>;
  if (!weather) return <div>Loading weather...</div>;

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h2 className="text-xl font-bold text-gray-700 mb-2">Weather</h2>
      <p className="text-gray-800">{weather.location.name}, {weather.location.region}</p>
      <p className="text-gray-600">{weather.current.condition.text}</p>
      <p className="text-gray-600">{weather.current.temp_f}°F</p>
    </div>
  );
};

export default WeatherFeed;
