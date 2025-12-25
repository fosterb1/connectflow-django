# ConnectFlow Pro - API v1 Documentation & Multi-Platform Guide

## 📋 Table of Contents
- [Project Evolution](#project-evolution)
- [API Architecture (v1)](#api-architecture-v1)
- [Authentication & Security](#authentication--security)
- [Core API Endpoints](#core-api-endpoints)
- [Real-time WebSocket API](#real-time-websocket-api)
- [Postman Testing Guide](#postman-testing-guide)
- [Demonstration Script](#demonstration-script)

---

## 🚀 Project Evolution

ConnectFlow Pro has evolved from a traditional Django website into a **Multi-Platform Communication Hub**. While the web dashboard continues to serve HTML, our new **REST API v1** allows native mobile apps (React Native/Flutter) and external integrations to interact with the exact same data source.

### **The December 2025 Leap**
*   **API v1 Foundation:** Modularized backend with dedicated serializers and viewsets.
*   **System Hardening:** Standardized media handling via Cloudinary `resource_type='auto'`.
*   **Data Integrity:** Implemented "Soft Delete" with real-time delete receipts.
*   **Mobile Readiness:** Built-in CORS and Firebase-ready authentication logic.

---

## 🏗️ API Architecture (v1)

### **Base URL**
`https://connectflow-pro.onrender.com/api/v1/`

### **Technology Stack**
- **Framework:** Django 5.2.9 + Django REST Framework 3.16
- **Real-time:** WebSockets via Django Channels + Redis
- **Media:** Cloudinary (Automatic Image/Video/Audio detection)
- **Database:** PostgreSQL (Render)

---

## 🔐 Authentication & Security

The API supports **Session-based Authentication** (for Web/Postman) and is architected for **Firebase/Token Authentication** (for Mobile).

### **Required Headers (for POST/PATCH/DELETE)**
```http
Content-Type: application/json
X-CSRFToken: {{CSRF_TOKEN}}
```

### **Organization Isolation**
The API automatically filters all requests. A user can **only** see data (Users, Teams, Channels) belonging to their own Organization.

---

## 📡 Core API Endpoints

### **1. User & Profile Management**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users/me/` | Get current authenticated user details |
| `GET` | `/users/` | List all users in your organization |
| `POST` | `/users/toggle_theme/` | Switch between LIGHT/DARK theme |

### **2. Organization Structure**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/organizations/` | Get current organization details & logo |
| `GET` | `/departments/` | List all departmental units |
| `GET` | `/teams/` | List team spaces you belong to |

### **3. Collaborative Projects**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/projects/` | List all active shared projects |
| `POST` | `/projects/` | Create a new cross-org project (Managers only) |
| `GET` | `/projects/{id}/` | Get project milestones and roster |

### **4. Channels & Messaging**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/channels/` | List all accessible chat channels |
| `GET` | `/channels/{id}/messages/` | Retrieve full message history |
| `POST` | `/messages/` | Send a new text or media message |
| `DELETE` | `/messages/{id}/` | **Soft Delete** a message (tracks who deleted) |

---

## ⚡ Real-time WebSocket API

### **WebSocket Connection**
`wss://connectflow-pro.onrender.com/ws/chat/{channel_id}/`

### **Real-time Event Types**
*   `chat_message`: New message received (including images/voice)
*   `message_update`: Sent when a message is edited
*   `message_delete`: **Delete Receipt** (Broadcasts `deleted_at` and `deleted_by`)
*   `presence`: Real-time Online/Offline status updates
*   `typing`: Real-time "User is typing..." indicator

---

## 🧪 Postman Testing Guide

### **Step 1: Setup Environment**
1. Create a variable `BASE_URL` = `https://connectflow-pro.onrender.com/api/v1`
2. Create a variable `CSRF_TOKEN`

### **Step 2: Authenticate**
1. Perform a regular Login via the web interface or `/accounts/login/`.
2. Postman will capture the session cookie automatically.
3. Use the `GET /api/v1/users/me/` to verify you are logged in.

### **Step 3: Test Soft Delete**
1. Send a message via `/api/v1/messages/`.
2. Delete it using `DELETE /api/v1/messages/{id}/`.
3. Check the database or perform a `GET`; the message will be hidden from regular results but archived in the backend.

---

## 🎓 Demonstration Script

**1. Headless Access (2 mins)**
Demonstrate fetching the user profile (`/users/me/`) via Postman to show the server identifies the user independently of the web UI.

**2. Media Robustness (3 mins)**
Demonstrate sending a voice message or image. Explain how `resource_type='auto'` in the backend prevents the server from crashing on non-image files.

**3. Data Integrity (3 mins)**
Demonstrate deleting a message. Show that the API returns a **Delete Receipt** with a timestamp, proving the "Soft Delete" mechanism is working.

**4. Multi-Org Scalability (2 mins)**
Show the list of Shared Projects (`/projects/`). Explain that the API allows guest organizations to connect their own mobile apps to this same project roster.

---

**This API v1 serves as the production-ready gateway for the ConnectFlow Pro ecosystem.** 🎓