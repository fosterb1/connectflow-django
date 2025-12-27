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
*   **SaaS Gatekeeper:** Integrated subscription limit enforcement (Users, Projects, Features) at the Serializer level.
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
- **Billing:** Multi-provider support (Paystack) with automated Webhooks
- **Media:** Cloudinary (Secure HTTPS + Universal file support)

---

## 📡 Core API Endpoints

### **1. User & Profile Management**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users/me/` | Get current authenticated user details |
| `GET` | `/users/` | List all users in your organization |
| `POST` | `/users/toggle_theme/` | Switch between LIGHT/DARK theme |

### **2. Organization & Billing**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/organizations/` | Get current organization details & subscription status |
| `GET` | `/departments/` | List all departmental units |
| `GET` | `/teams/` | List team spaces you belong to |

### **3. Collaborative Projects & Analytics**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/projects/` | List all active shared projects |
| `POST` | `/projects/` | Create workspace (**Gatekeeper protected**: Checks plan project limit) |
| `GET` | `/projects/{id}/` | Get project milestones and roster |
| `GET` | `/projects/{id}/analytics/` | **Premium Feature**: Returns statistics (Forbidden on lower tiers) |

### **4. Channels & Messaging**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/channels/` | List all accessible chat channels |
| `GET` | `/channels/{id}/messages/` | Retrieve full message history |
| `POST` | `/messages/` | Send text or media (**Universal file support**) |
| `DELETE` | `/messages/{id}/` | **Soft Delete** a message (tracks who deleted) |

---

## 🛡️ SaaS Gatekeeper & Business Logic

The API is architected to protect your business model automatically.

### **1. Plan Limit Enforcement**
When a `POST` request is sent to `/projects/`, the **SharedProjectSerializer** validates the organization's subscription plan. If the limit is exceeded, the API returns:
*   **Status:** `400 Bad Request`
*   **Message:** `"Organization has reached the limit of X project(s)..."`

### **2. Feature Locking**
Endpoints like `/projects/{id}/analytics/` use the **HasSubscriptionFeature** permission class. If the organization's plan has `has_analytics=False`, the API returns:
*   **Status:** `403 Forbidden`
*   **Message:** `"Project Analytics is a premium feature."`

---

## 🧪 Postman & Browser Testing Guide

### **Method A: The Browser (Easiest)**
1. Log into the ConnectFlow web dashboard.
2. In the same browser, navigate to: `https://connectflow-pro.onrender.com/api/v1/`
3. You will see the **Django REST Framework Browsable API**.
4. You can click on endpoints and even perform `POST/PUT` actions using the forms at the bottom of the page.

### **Method B: Postman (Professional)**
1. **Login:** Perform a `POST` to `/accounts/login/` with your Firebase token (or simply log in via the web app first, as Postman will share your browser's cookies if you use the Postman Interceptor).
2. **CSRF Protection:** For `POST/PATCH/DELETE` requests, you must include the `X-CSRFToken` header.
   *   Get the token from your browser cookies (`csrftoken`).
3. **Environment Setup:**
   *   `BASE_URL`: `https://connectflow-pro.onrender.com/api/v1`
   *   **Auth:** Set to "No Auth" if using browser cookies, or "Bearer Token" if using Firebase ID tokens.
4. **Testing Analytics:**
   *   Navigate to `{{BASE_URL}}/projects/[YOUR_PROJECT_ID]/analytics/`.
   *   Observe how the response changes when you toggle the `has_analytics` benefit in the **Platform Admin Suite**.

---

## 🎓 Demonstration Script

**1. Subscription Gatekeeper (3 mins)**
Attempt to create a project via the API while on a "Starter" plan. Show the `400 Bad Request`. Upgrade the plan in the Platform Admin, try again, and show the `201 Created` success.

**2. Premium Feature Lock (2 mins)**
Request `/projects/{id}/analytics/` from a basic account. Show the `403 Forbidden`. This proves the API is aware of the business tiers.

**3. Universal Media Access (2 mins)**
Upload a non-image file (PDF/ZIP) and show the generated URL. Explain that the API forces **HTTPS** and uses **Raw Storage** to ensure the files are accessible and secure.

**4. Real-time Presence (2 mins)**
Open two browser windows. Show how changing status in one is reflected via the WebSocket API in the other instantly.

---

**This API v1 serves as the production-ready gateway for the ConnectFlow Pro ecosystem.** 🎓