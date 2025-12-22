# ConnectFlow Pro - API Documentation & Postman Guide

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [API Architecture](#api-architecture)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Postman Setup](#postman-setup)
- [Testing with Postman](#testing-with-postman)

---

## 🎯 Project Overview

**ConnectFlow Pro** is a real-time organizational communication platform built with Django, featuring:
- Role-based access control (Super Admin, Department Head, Team Manager, Team Member)
- Real-time messaging with WebSockets (Django Channels)
- Hierarchical organizational structure
- File uploads and voice messages
- Progressive Web App (PWA) features

---

## 🏗️ API Architecture

### **Technology Stack**
- **Backend:** Django 5.2.9
- **Database:** PostgreSQL (Production) / SQLite (Development)
- **Real-time:** Django Channels + WebSockets
- **Authentication:** Django Session Authentication
- **File Storage:** Cloudinary (Production) / Local (Development)

### **API Style**
- **Type:** RESTful + WebSocket (Hybrid)
- **Format:** JSON
- **Authentication:** Session-based (CSRF tokens required)

---

## 🔐 Authentication

### **Login Flow**

**Endpoint:** `POST /accounts/login/`

**Request Body:**
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

**Response (Success):**
```json
{
    "success": true,
    "redirect": "/accounts/dashboard/"
}
```

**Authentication Method:**
- Session-based authentication
- CSRF token protection
- Cookies used for session management

---

## 📡 API Endpoints

### **1. Authentication APIs**

#### **Login**
```
POST /accounts/login/
Content-Type: application/json

Body:
{
    "username": "john_doe",
    "password": "SecurePass123"
}

Response:
{
    "success": true,
    "redirect": "/accounts/dashboard/"
}
```

#### **Logout**
```
POST /accounts/logout/

Response: Redirects to login page
```

#### **Register**
```
POST /accounts/register/
Content-Type: application/json

Body:
{
    "username": "new_user",
    "email": "user@example.com",
    "password1": "SecurePass123",
    "password2": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "TEAM_MEMBER"
}

Response:
{
    "success": true,
    "redirect": "/accounts/dashboard/"
}
```

---

### **2. Organization APIs**

#### **Create Organization**
```
POST /organization/create/
Content-Type: application/json

Headers:
X-CSRFToken: <csrf_token>

Body:
{
    "name": "Tech Company Inc",
    "description": "A technology company"
}

Response:
{
    "success": true,
    "organization_id": 1,
    "redirect": "/organization/1/"
}
```

#### **Get Organization Details**
```
GET /organization/<id>/

Response:
{
    "id": 1,
    "name": "Tech Company Inc",
    "description": "A technology company",
    "created_at": "2025-12-22T00:00:00Z",
    "member_count": 5,
    "departments": [...]
}
```

#### **Create Department**
```
POST /organization/<id>/department/create/
Content-Type: application/json

Body:
{
    "name": "Engineering",
    "description": "Software development team",
    "head": <user_id>
}
```

#### **Create Team**
```
POST /organization/department/<dept_id>/team/create/
Content-Type: application/json

Body:
{
    "name": "Backend Team",
    "description": "Django developers",
    "manager": <user_id>
}
```

---

### **3. Channel APIs**

#### **List Channels**
```
GET /channels/

Response:
[
    {
        "id": 1,
        "name": "general",
        "channel_type": "OFFICIAL",
        "description": "Company-wide announcements",
        "is_private": false,
        "member_count": 25,
        "created_at": "2025-12-22T00:00:00Z"
    },
    ...
]
```

#### **Create Channel**
```
POST /channels/create/
Content-Type: application/json

Body:
{
    "name": "project-alpha",
    "channel_type": "PROJECT",
    "description": "Project Alpha discussions",
    "is_private": false,
    "organization": <org_id>
}

Response:
{
    "success": true,
    "channel_id": 5,
    "redirect": "/channels/5/"
}
```

#### **Get Channel Details**
```
GET /channels/<id>/

Response:
{
    "id": 5,
    "name": "project-alpha",
    "channel_type": "PROJECT",
    "description": "Project Alpha discussions",
    "member_count": 10,
    "messages": [
        {
            "id": 1,
            "sender": "john_doe",
            "content": "Hello team!",
            "timestamp": "2025-12-22T10:30:00Z",
            "reactions": {"👍": 2, "❤️": 1}
        },
        ...
    ]
}
```

---

### **4. Messaging APIs**

#### **Send Message (HTTP)**
```
POST /channels/<channel_id>/send/
Content-Type: multipart/form-data

Headers:
X-CSRFToken: <csrf_token>

Body (Form Data):
content: "Hello everyone!"
file_upload: <file> (optional)
voice_message: <audio_file> (optional)
voice_duration: 15 (optional, in seconds)

Response:
{
    "success": true,
    "message_id": 123,
    "content": "Hello everyone!",
    "timestamp": "2025-12-22T10:30:00Z",
    "sender_avatar": "https://..."
}
```

#### **Get Channel Messages**
```
GET /channels/<id>/messages/?page=1

Response:
{
    "count": 50,
    "next": "/channels/5/messages/?page=2",
    "previous": null,
    "results": [
        {
            "id": 123,
            "sender": {
                "id": 1,
                "username": "john_doe",
                "avatar": "https://..."
            },
            "content": "Hello everyone!",
            "timestamp": "2025-12-22T10:30:00Z",
            "attachments": [],
            "voice_message": null,
            "reactions": {"👍": 2}
        },
        ...
    ]
}
```

#### **Edit Message**
```
POST /channels/message/<message_id>/edit/
Content-Type: application/json

Body:
{
    "content": "Updated message content"
}

Response:
{
    "success": true,
    "content": "Updated message content"
}
```

#### **Delete Message**
```
POST /channels/message/<message_id>/delete/

Response:
{
    "success": true
}
```

#### **React to Message**
```
POST /channels/message/<message_id>/react/
Content-Type: application/json

Body:
{
    "emoji": "👍"
}

Response:
{
    "success": true,
    "reactions": {"👍": 3, "❤️": 1}
}
```

---

### **5. User Profile APIs**

#### **Get Profile**
```
GET /accounts/profile/

Response:
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "TEAM_MEMBER",
    "avatar": "https://res.cloudinary.com/...",
    "bio": "Backend developer",
    "phone": "+1234567890",
    "status": "ONLINE"
}
```

#### **Update Profile**
```
POST /accounts/profile/settings/
Content-Type: multipart/form-data

Body:
first_name: "John"
last_name: "Doe"
email: "john@example.com"
avatar: <image_file> (optional)

Response: Redirects to profile page
```

---

### **6. WebSocket API (Real-time Messaging)**

#### **WebSocket Connection**
```
URL: ws://localhost:8000/ws/channel/<channel_id>/
OR
URL: wss://your-domain.com/ws/channel/<channel_id>/

Connection requires:
- Active session (logged in)
- Member of the channel
```

#### **Send Message (WebSocket)**
```javascript
// Connect
const socket = new WebSocket('ws://localhost:8000/ws/channel/5/');

// Send message
socket.send(JSON.stringify({
    type: 'chat_message',
    message: 'Hello from WebSocket!'
}));

// Receive message
socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log('Message:', data.message);
};
```

#### **Typing Indicator**
```javascript
// Send typing status
socket.send(JSON.stringify({
    type: 'typing',
    is_typing: true
}));

// Receive typing notification
{
    "type": "typing",
    "user": "john_doe",
    "is_typing": true
}
```

---

## 🧪 Postman Setup

### **Step 1: Import Collection**

Create a new Postman collection named "ConnectFlow Pro API"

### **Step 2: Set Environment Variables**

Create environment variables:
```
BASE_URL: http://localhost:8000
OR
BASE_URL: https://connectflow-pro.onrender.com

CSRF_TOKEN: (will be set after login)
SESSION_COOKIE: (automatically handled)
```

### **Step 3: Configure CSRF Token**

Add this to your Pre-request Script (Collection level):
```javascript
// Get CSRF token from cookie
const csrfCookie = pm.cookies.get('csrftoken');
if (csrfCookie) {
    pm.environment.set('CSRF_TOKEN', csrfCookie);
}
```

### **Step 4: Add Headers**

For POST/PUT/DELETE requests, add headers:
```
Content-Type: application/json
X-CSRFToken: {{CSRF_TOKEN}}
```

---

## 🎯 Testing with Postman

### **Test Flow 1: User Registration & Login**

**1. Register User**
```
POST {{BASE_URL}}/accounts/register/
Body (JSON):
{
    "username": "test_user",
    "email": "test@example.com",
    "password1": "TestPass123",
    "password2": "TestPass123",
    "first_name": "Test",
    "last_name": "User",
    "role": "TEAM_MEMBER"
}
```

**2. Login**
```
POST {{BASE_URL}}/accounts/login/
Body (JSON):
{
    "username": "test_user",
    "password": "TestPass123"
}

✅ Save the session cookie automatically
✅ Get CSRF token from response headers
```

**3. View Dashboard**
```
GET {{BASE_URL}}/accounts/dashboard/

✅ Should return HTML or redirect (authenticated)
```

---

### **Test Flow 2: Organization Setup**

**1. Create Organization**
```
POST {{BASE_URL}}/organization/create/
Headers:
X-CSRFToken: {{CSRF_TOKEN}}

Body:
{
    "name": "Test Corp",
    "description": "Testing organization"
}
```

**2. Create Department**
```
POST {{BASE_URL}}/organization/1/department/create/
Body:
{
    "name": "Engineering",
    "description": "Dev team"
}
```

**3. Create Team**
```
POST {{BASE_URL}}/organization/department/1/team/create/
Body:
{
    "name": "Backend Team",
    "description": "Django developers"
}
```

---

### **Test Flow 3: Channels & Messaging**

**1. Create Channel**
```
POST {{BASE_URL}}/channels/create/
Body:
{
    "name": "test-channel",
    "channel_type": "TEAM",
    "description": "Test channel for API demo",
    "is_private": false
}
```

**2. List Channels**
```
GET {{BASE_URL}}/channels/
```

**3. Send Message**
```
POST {{BASE_URL}}/channels/1/send/
Content-Type: multipart/form-data

Form Data:
content: "Hello from Postman!"
```

**4. Get Messages**
```
GET {{BASE_URL}}/channels/1/messages/
```

**5. React to Message**
```
POST {{BASE_URL}}/channels/message/1/react/
Body:
{
    "emoji": "👍"
}
```

**6. Edit Message**
```
POST {{BASE_URL}}/channels/message/1/edit/
Body:
{
    "content": "Updated message from Postman!"
}
```

**7. Delete Message**
```
POST {{BASE_URL}}/channels/message/1/delete/
```

---

### **Test Flow 4: File Uploads**

**1. Upload Avatar**
```
POST {{BASE_URL}}/accounts/profile/settings/
Content-Type: multipart/form-data

Form Data:
first_name: "Test"
last_name: "User"
avatar: <select image file>

✅ Image will upload to Cloudinary (production)
✅ Returns updated profile
```

**2. Send Message with File**
```
POST {{BASE_URL}}/channels/1/send/
Content-Type: multipart/form-data

Form Data:
content: "Check this file!"
file_upload: <select file>

✅ File stored on Cloudinary
✅ Message includes attachment URL
```

---

## 🔧 Common Issues & Solutions

### **Issue 1: CSRF Token Error**

**Error:** `403 Forbidden - CSRF verification failed`

**Solution:**
1. Make sure you're logged in first
2. Get CSRF token from cookies
3. Add to header: `X-CSRFToken: <token>`

### **Issue 2: Unauthorized**

**Error:** `401 Unauthorized` or redirects to login

**Solution:**
1. Login first to get session cookie
2. Ensure cookies are enabled in Postman
3. Check session hasn't expired

### **Issue 3: WebSocket Connection Failed**

**Solution:**
1. Use WebSocket client (not regular HTTP)
2. Include session cookie in connection
3. Ensure channel membership

---

## 📚 Additional Resources

### **API Response Codes**

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid data |
| 401 | Unauthorized | Not logged in |
| 403 | Forbidden | No permission |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Internal error |

### **Channel Types**

- `OFFICIAL` - Company-wide announcements (read-only for most)
- `DEPARTMENT` - Department-specific discussions
- `TEAM` - Team collaboration spaces
- `PROJECT` - Project-specific channels
- `PRIVATE` - Invite-only private groups

### **User Roles**

- `SUPER_ADMIN` - Full system access
- `DEPT_HEAD` - Manages department
- `TEAM_MANAGER` - Manages team
- `TEAM_MEMBER` - Regular user

---

## 🎓 For Demonstration

### **Quick Demo Script**

**1. Setup (2 minutes)**
```
- Register user
- Login
- Create organization
```

**2. Organization Structure (3 minutes)**
```
- Create department
- Create team
- Show hierarchical structure
```

**3. Communication (5 minutes)**
```
- Create channels
- Send messages
- Upload files
- Voice messages
- Emoji reactions
- Real-time updates (WebSocket)
```

**4. Advanced Features (3 minutes)**
```
- Edit/delete messages
- Private channels
- Role-based access
- File storage (Cloudinary)
```

**Total Demo Time: ~15 minutes**

---

## 🚀 Running Locally for Demo

```bash
# Clone repository
git clone https://github.com/fosterboadi/connectflow-django.git
cd connectflow-django

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Access at: http://localhost:8000
```

---

**This API documentation provides everything needed to demonstrate the ConnectFlow Pro platform's capabilities for your Django backend development course assignment.** 🎓
