# ConnectFlow Pro - REST API v1 Reference

## 🔐 Authentication
ConnectFlow Pro uses **Firebase ID Tokens** for secure access.

### **Authorization Header**
All requests must include the following header:
```http
Authorization: Bearer <YOUR_FIREBASE_ID_TOKEN>
```

---

## 📡 API Endpoints

### **1. Identity & Profile**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/users/me/` | Returns current user details, role, and organization context. |
| `GET` | `/api/v1/users/` | List all members within your organization. |
| `POST` | `/api/v1/users/toggle_theme/` | Toggle between LIGHT and DARK UI modes. |

### **2. Organization Structure**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/organizations/` | View organization metadata (branding, industry, status). |
| `GET` | `/api/v1/departments/` | List all departmental units. |
| `GET` | `/api/v1/teams/` | List all internal teams. |

### **3. Collaborative Projects**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/projects/` | List workspaces shared between organizations. |
| `POST` | `/api/v1/projects/` | Launch workspace (**Gatekeeper**: Validates plan limits). |
| `GET` | `/api/v1/projects/{id}/` | Retrieve roster, milestones, and status. |
| `GET` | `/api/v1/projects/{id}/analytics/`| **Premium**: Returns collaboration maps and KPI data. |

### **4. Real-time Communication**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/channels/` | List all accessible private and project channels. |
| `GET` | `/api/v1/channels/{id}/messages/` | Retrieve full message history. |
| `POST` | `/api/v1/messages/` | Send message (**Universal Support**: text, image, file, voice). |
| `DELETE` | `/api/v1/messages/{id}/` | **Soft Delete**: Archives message and broadcasts delete receipt. |

### **5. SaaS Management & Billing**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/billing/plans/` | List available subscription tiers and benefits. |
| `POST` | `/api/v1/billing/paystack/{plan_id}/` | Initialize Paystack transaction for tier upgrade. |

---

## 🛡️ SaaS Gatekeeper (Business Logic)
The API enforces organization-level limits and feature locks at the logic layer:
*   **Plan Validation:** `POST` requests to create projects or users are blocked if the organization's plan limit is reached (`400 Bad Request`).
*   **Feature Locking:** Premium endpoints (like Analytics) return `403 Forbidden` if the `has_analytics` toggle is disabled for the organization's current tier.

---

## 🧪 Testing in Console
Since you are already logged into the dashboard, you can test these directly in your browser console:
```javascript
fetch('/api/v1/users/me/').then(res => res.json()).then(console.table);
```
