# ConnectFlow Pro: Revenue & Scaling Strategy

## 1. Operational Cost Analysis
To build a sustainable subscription model, we must first understand the "Cost of Goods Sold" (COGS) for each organization hosted on ConnectFlow Pro.

### Primary Cost Drivers
*   **Cloudinary (Storage & Bandwidth):** 
    *   *Free Tier:* 25 Credits (approx. 25GB storage or bandwidth).
    *   *Scale Tier:* $99/mo for 225 Credits.
    *   **Strategy:** Storage limits in tiers must be strictly enforced to avoid Cloudinary overages.
*   **Database (PostgreSQL):** 
    *   As organizations grow, the number of messages and "Shared Project" relations increases.
    *   **Strategy:** Row counts aren't limited in our app, but we should limit the *number of projects* to keep DB indices performant.
*   **WebSocket Infrastructure (Django Channels/Redis):** 
    *   Real-time messaging requires persistent connections. More users = higher RAM usage on the server.
    *   **Strategy:** Limit "User Caps" per tier to prevent a single organization from monopolizing the WebSocket worker pool.

---

## 2. Market Benchmarking
How we compare to industry leaders (Slack, Monday.com, Asana):
*   **Slack:** Uses per-user pricing ($7.25/user).
*   **Basecamp:** Uses flat-fee pricing ($15/user or $299/mo unlimited).
*   **ConnectFlow Pro USP:** Our unique "Shared Projects" (multi-org collaboration) allows us to charge based on **Collaboration Capacity** rather than just seats.

---

## 3. Proposed Subscription Tiers (Implementation Guide)

| Tier Name | Purpose | Price (USD) | User Cap | Project Cap | Storage | Features |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Community** | Small teams / Startups | $0 | 10 | 1 | 500 MB | Core Messaging, Task Boards |
| **Professional** | Growing businesses | $29/mo | 50 | 10 | 10 GB | Analytics, Project Milestones |
| **Business** | Mid-size corporations | $89/mo | 250 | 50 | 100 GB | Custom Branding, Priority Support |
| **Enterprise** | Large scale ventures | $299/mo | Unlimited | Unlimited | 1 TB | Dedicated Server, Full Access |

---

## 4. Future Scaling & Monetization
As the platform matures, we should look beyond flat tiers into **Usage-Based Monetization**:

### A. The "Storage Add-on" Model
Instead of forcing a user to upgrade to "Business" just for storage, we can sell **Storage Packs**:
*   +$10/mo for 50GB extra.
*   +$50/mo for 500GB extra.

### B. Joint Venture Licensing
Since ConnectFlow Pro allows Organizations to collaborate:
*   Charge a "Collaboration Fee" when more than 3 independent organizations join a single `SharedProject`.
*   This targets high-value consultants and multi-firm construction/tech projects.

### C. Analytics as a Premium Service
Deep-dive analytics into team productivity and project velocity are high-value for management. 
*   **Recommendation:** Keep the basic dashboard for all, but put the "Organization Network Map" and "Velocity Charts" behind the $89/mo Business tier.

---

## 5. Action Plan for Platform Admins
1.  **Cleanup:** Delete current test plans in the Platform Admin panel.
2.  **Seeding:** Create the **Community ($0)** plan first to ensure the "Auto-assign Free Tier" logic works for new signups.
3.  **Tier Entry:** Create the **Professional** and **Business** tiers using the new GB unit selector.
4.  **Paystack Sync:** Ensure the `paystack_plan_code` generated in your Paystack dashboard is copied into the corresponding tier in ConnectFlow.

---
*Document Version: 1.0.0*  
*Last Updated: December 27, 2025*
