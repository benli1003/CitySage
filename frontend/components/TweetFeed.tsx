import React from 'react';
import {useEffect, useState} from 'react'
import axios from 'axios'

interface Tweet {
    id: string
    text: string
    user: string
    timestamp: string
}

export default function() {
    const [tweets, setTweets] = useState<Tweet[]> ([])

    useEffect(() => {
        const fetchTweets = async () => {
            try {
                const response = await axios.get('http://localhost:5000/api/tweets/latest')
                setTweets(response.data.tweets)
            } catch (error) {
                console.error(error)
            }
        }

        fetchTweets
        const interval = setInterval(fetchTweets, 30000) // Fetch tweets every 30 seconds

        return () => clearInterval(interval)
    }, [])
    
    return (
        <div>
          {tweets.map((tweet) => (
            <div key={tweet.id} style={{ border: '1px solid gray', padding: '10px', marginBottom: '10px' }}>
              <div><strong>@{tweet.user}</strong></div>
              <div style={{ fontSize: '0.8rem', color: 'gray' }}>{tweet.timestamp}</div>
              <p>{tweet.text}</p>
            </div>
          ))}
        </div>
      )
    }