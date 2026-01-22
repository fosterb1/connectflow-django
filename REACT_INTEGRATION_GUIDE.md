# React Integration Guide for ConnectFlow API

This guide explains how to integrate your React frontend with the ConnectFlow Django backend deployed on Render.

## 1. Environment Configuration

Create a `.env` file in your React project root:

```env
REACT_APP_API_URL=https://connectflow-pro.onrender.com/api/v1
REACT_APP_WS_URL=wss://connectflow-pro.onrender.com/ws
```

## 2. Authentication System

The backend uses **Django Rest Framework Token Authentication**.

### API Utility (`src/api/axios.js`)

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach Auth Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

export default api;
```

### Auth Context (`src/context/AuthContext.js`)

```javascript
import React, { createContext, useState, useEffect, useContext } from 'react';
import api from '../api/axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchMe();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchMe = async () => {
    try {
      const res = await api.get('/users/me/');
      setUser(res.data);
    } catch (err) {
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const res = await api.post('/login/', { email, password });
    localStorage.setItem('token', res.data.token);
    setUser(res.data.user);
    return res.data;
  };

  const logout = async () => {
    await api.post('/logout/');
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

## 3. API Endpoints Reference

| Feature | Endpoint | Method | Auth Required |
|---------|----------|--------|---------------|
| Login | `/login/` | POST | No |
| Logout | `/logout/` | POST | Yes |
| Profile | `/users/me/` | GET | Yes |
| Organizations| `/organizations/`| GET | Yes |
| Channels | `/channels/` | GET | Yes |
| Messages | `/messages/` | GET/POST | Yes |

## 4. Real-time Integration (WebSockets)

Since the backend uses **Django Channels**, use the following pattern for chat or notifications:

```javascript
const socket = new WebSocket(
  `${process.env.REACT_APP_WS_URL}/chat/${channelId}/?token=${localStorage.getItem('token')}`
);

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('New message:', data);
};

const sendMessage = (text) => {
  socket.send(JSON.stringify({
    'message': text,
    'action': 'chat_message'
  }));
};
```

## 5. Deployment Notes (Render.com)

1. **CORS:** The backend is already configured with `CORS_ALLOW_ALL_ORIGINS = True`.
2. **HTTPS/WSS:** Render enforces SSL. Always use `https://` for API and `wss://` for WebSockets.
3. **Avatars:** User avatars are served via Cloudinary. The `avatar` field in the user object will return a full URL.
