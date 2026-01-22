# React Screens & API Implementation Guide

This document outlines how to build the core screens of the ConnectFlow React application and which APIs to consume for each.

## 1. Dashboard (The Command Center)
**Goal:** A high-level overview of the user's organization, recent notifications, and quick actions.

### Data to Fetch:
- **Current User:** `GET /api/v1/users/me/`
- **Organization Stats:** `GET /api/v1/organizations/`
- **Recent Notifications:** Handled via WebSocket (`ws/notifications/`)

### Key Components:
- `StatCard`: Displays active tickets, total team members, and current KPI score.
- `NotificationBell`: Real-time updates using the `notifications_{user_id}` group.

---

## 2. Organization & Teams
**Goal:** Manage departments, teams, and view the hierarchy.

### Data to Fetch:
- **Departments:** `GET /api/v1/departments/`
- **Teams:** `GET /api/v1/teams/`
- **Create Team:** `POST /api/v1/teams/`

### React Implementation:
Use a nested layout. Selecting a **Department** should filter the **Teams** list.
```javascript
// Example: Fetching Teams for a specific Department
const fetchTeams = (deptId) => api.get(`/teams/?department=${deptId}`);
```

---

## 3. Chat System (Real-time)
**Goal:** Channel-based communication with advanced features like voice notes and task creation.

### Data to Fetch:
- **Channel List:** `GET /api/v1/channels/`
- **Message History:** `GET /api/v1/channels/{id}/messages/`
- **Pinned Messages:** `POST /api/v1/messages/{id}/pin/`
- **Star Message:** `POST /api/v1/messages/{id}/star/`

### Real-time Logic (WebSocket):
Connect to `${WS_URL}/chat/${channelId}/?token=${token}`.
- **On Message:** Append to state using a functional update `setMessages(prev => [...prev, newMessage])`.
- **Special Actions:** 
    - `forward`: `POST /api/v1/messages/{id}/forward/` (Pass `target_channel_id`).
    - `create_task`: `POST /api/v1/messages/{id}/create_task/` (Converts a chat message into a project task).

---

## 4. Video & Audio Calls (WebRTC)
**Goal:** WhatsApp-style calling within the platform.

### API Endpoints:
- **Initiate Call:** `POST /calls/initiate/` (Returns `room_id`).
- **Call Status:** `GET /calls/{id}/status/`
- **End/Reject:** `POST /calls/{id}/end/` or `POST /calls/{id}/reject/`

### Integration Steps:
1. **Notification:** Listen for `type: 'send_notification'` where `notification_type: 'CALL'`.
2. **WebRTC:** Use the `room_id` to join a signalling group via WebSocket.
3. **ICE Servers:** Use the STUN/TURN config provided by the backend to handle NAT traversal.

---

## 5. Performance & KPI Tracking
**Goal:** Professional growth tracking for employees and managers.

### Data to Fetch:
- **My Dashboard:** `GET /performance/api/my-performance/`
- **KPI Metrics:** `GET /performance/api/kpi-metrics/`
- **Responsibilities:** `POST /performance/complete-responsibility/{id}/`

### Implementation Tip:
Build a **"KPI Portfolio"** screen where users see their "Monthly Progress" vs "Target Value". Use a library like `recharts` to visualize the `final_score` history.

---

## 6. Support Ticketing
**Goal:** Internal helpdesk for users.

### Data to Fetch:
- **My Tickets:** `GET /api/v1/tickets/`
- **Ticket Details:** `GET /api/v1/tickets/{id}/`
- **Reply to Ticket:** `POST /api/v1/tickets/{id}/add_message/`

---

## 7. Global State Management Recommendations

| State Part | Recommended Tool | Why? |
|------------|------------------|------|
| Auth | React Context | Needs to be available everywhere. |
| API Data | React Query (TanStack) | Handles caching, loading, and auto-refetching. |
| WebSockets | Custom Hook (`useSocket`) | Handles auto-reconnect and cleanup on unmount. |
| Calling | User Stream (Global Ref) | You don't want to lose a call when navigating pages. |

---

## 8. Summary of URL Structure for React Router
- `/login` -> Login Page
- `/dashboard` -> Home Overview
- `/chat/:channelId` -> Chat Interface
- `/teams` -> Organization Management
- `/performance` -> KPI Dashboard
- `/support` -> Ticket List
- `/call/:callId` -> Active Call Room (FullScreen)
