# 🎓 ConnectFlow Pro: The Master Presentation Script

This document is your **live script** for the technical presentation. It is designed to be followed step-by-step to show off the platform's security, business logic, and scalability using **Postman**.

---

## 🛠 PHASE 0: Preparation (The "Master Key")
*Before the presentation starts, you need to get your identity token.*

1.  **Open Browser:** Log into `https://connectflow-pro.onrender.com`.
2.  **Open Console:** Press **F12** (or Right-click > Inspect > Console).
3.  **Get Token:** Paste this code and hit Enter:
    ```javascript
    firebase.auth().currentUser.getIdToken().then(console.log)
    ```
4.  **Copy Result:** You will see a very long string starting with `eyJhbG...`. Keep this ready.

---

## 🚀 PHASE 1: The "Identity" Handshake
*Goal: Prove that the API can identify you independently of the web dashboard.*

1.  **In Postman:** Create a new **GET** request.
2.  **URL:** `https://connectflow-pro.onrender.com/api/v1/users/me/`
3.  **The "Auth" Tab:** 
    *   Click the **Auth** tab (under the URL bar).
    *   Change Type to **Bearer Token**.
    *   Paste your long token from Phase 0.
4.  **Action:** Click **Send**.
5.  **What to Say:** *"I am starting by proving our Headless architecture. Even without a browser, the API identifies me, my organization (ConnectFlow Corp), and my role as a Super Admin. This token-based security is exactly how our future mobile apps will communicate."*

---

## 🔒 PHASE 2: Data Isolation & Multi-Tenancy
*Goal: Show that users only see what they are authorized to see.*

1.  **In Postman:** New tab, **GET** request.
2.  **URL:** `https://connectflow-pro.onrender.com/api/v1/projects/`
3.  **Auth:** (Ensure Bearer Token is still there).
4.  **Action:** Click **Send**.
5.  **What to Say:** *"Security is baked into our data layer. Even if there are 10,000 projects in the database, the API automatically filters the results. I only see the projects belonging to my organization. This is true secure multi-tenancy."*

---

## 🛡️ PHASE 3: The SaaS Gatekeeper (The Upgrade Demo)
*Goal: Show how the app protects your revenue by locking premium features.*

1.  **Pick a Project:** From the result in Phase 2, copy one project `id` (e.g., `550e8400...`).
2.  **In Postman:** New tab, **GET** request.
3.  **URL:** `https://connectflow-pro.onrender.com/api/v1/projects/[PASTE_ID_HERE]/analytics/`
4.  **Action:** Click **Send**.
5.  **If it fails (403):** *"Here we see our monetization engine. My organization is on a 'Basic' plan, so the API explicitly blocks access to advanced Analytics. To see this data, the client must upgrade via Paystack."*
6.  **If it succeeds:** *"Because I am a Super Admin, the Gatekeeper grants me full access to premium KPI data and collaboration maps."*

---

## 🏗️ PHASE 4: Headless Creation (The "Action" Test)
*Goal: Prove you can build a company structure entirely via API.*

1.  **In Postman:** New tab, change method to **POST**.
2.  **URL:** `https://connectflow-pro.onrender.com/api/v1/departments/`
3.  **The "Body" Tab:**
    *   Select **raw**.
    *   On the far right, change "Text" to **JSON**.
4.  **Paste this:**
    ```json
    { 
      "name": "Global Innovation Lab", 
      "description": "Created during the live demo" 
    }
    ```
5.  **Action:** Click **Send**.
6.  **Confirmation:** Go to your web dashboard and refresh the **Organization** page. The new department will be there!
7.  **What to Say:** *"Finally, we are showing that ConnectFlow is a true platform. I just created a new organizational unit via the API, and it appeared instantly on our web dashboard. This proves our backend is ready to power any integration."*

---

## 💰 PHASE 5: Monetization (Paystack)
*Goal: Show the path to profit.*

1.  **URL:** `GET https://connectflow-pro.onrender.com/api/v1/billing/plans/`
2.  **What to Say:** *"We close with the business model. Our API serves our product catalog directly. Any organization can view these tiers and initiate a secure Paystack checkout to unlock the premium features we saw earlier."*

---

## 🏁 Final Conclusion
*"ConnectFlow Pro is more than a tool; it is a secure, scalable, and profitable infrastructure for modern joint-venture collaboration."*
