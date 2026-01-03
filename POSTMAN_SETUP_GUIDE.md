# ConnectFlow Pro - POSTMAN SETUP (STEP-BY-STEP)

## ⚡ WHAT YOU NEED
1. **Postman installed** - Download from postman.com
2. **Your deployed app URL** - e.g., `https://connectflow.onrender.com`
3. **A Firebase auth token** - Get it from your browser after logging in

---

## 🎯 STEP 1: LOGIN TO GET YOUR TOKEN

**NOW IT'S SUPER EASY!** Just login with email and password in Postman.

### In Postman - Create Login Request

1. Create a new request (don't put it in any folder yet)
2. Name: `Login - Get Token`
3. Method: **POST**
4. URL: `https://connectflow.onrender.com/api/v1/login/`
5. Go to **"Body"** tab → Select **"raw"** → Select **"JSON"**
6. Paste this:
```json
{
  "email": "your-email@example.com",
  "password": "your-password"
}
```
7. Click **"Send"**

### You'll get a response like:
```json
{
  "token": "9a7f8b6c5d4e3f2g1h0i9j8k7l6m5n4o3p2q1",
  "user": {
    "id": 1,
    "email": "your-email@example.com",
    "first_name": "John",
    "last_name": "Doe",
    ...
  }
}
```

**COPY THAT TOKEN!** You'll use it for all other requests.

---

## 🎯 STEP 2: SETUP POSTMAN

### 2.1 Create Collection
1. Open Postman
2. Click **"New"** → **"Collection"**
3. Name: `ConnectFlow API`
4. Click **"Create"**

### 2.2 Setup Environment
1. Click **"Environments"** (left sidebar)
2. Click **"+"** to create new environment
3. Name: `ConnectFlow Production`
4. Add these variables:

| Variable | Current Value |
|----------|---------------|
| `base_url` | `https://connectflow.onrender.com/api/v1` |
| `token` | *LEAVE EMPTY - will be set after login* |

5. Click **"Save"**
6. Select this environment from dropdown (top right)

### 2.3 Set Collection Authorization
1. Click on your `ConnectFlow API` collection
2. Go to **"Authorization"** tab
3. Type: Select **"Bearer Token"**
4. Token: Type `{{token}}`
5. Click **"Save"**

✅ **DONE! Now all requests will use your token automatically.**

---

## 🎯 STEP 3: ADD YOUR API ENDPOINTS

### CREATE FOLDERS (Right-click collection → Add Folder)

1. **Authentication** ← Put your login request here
2. **Users**
3. **Organizations**
4. **Projects**  
5. **Channels**
6. **Messages**
7. **Support Tickets**

---

## 📁 FOLDER 1: AUTHENTICATION

### Request 1: Login (GET TOKEN)
- Name: `Login - Get Token`
- Method: **POST**
- URL: `{{base_url}}/login/`
- Authorization: **No Auth** (this is the login, no token needed yet)
- Body: **raw** → **JSON**
```json
{
  "email": "your-email@example.com",
  "password": "your-password"
}
```
- **After sending:** Copy the token from response
- Go to Environments → Click on your environment → Paste token in `token` variable

### Request 2: Logout
- Name: `Logout`
- Method: **POST**
- URL: `{{base_url}}/logout/`
- Authorization: Inherit from parent (uses Bearer token)

---

## 📁 FOLDER 2: USERS

### Request 1: Get My Profile
- Right-click "Users" folder → **Add Request**
- Name: `Get My Profile`
- Method: **GET**
- URL: `{{base_url}}/users/me/`
- Click **"Send"**

### Request 2: List All Users
- Name: `List All Users`
- Method: **GET**
- URL: `{{base_url}}/users/`

### Request 3: Get User By ID
- Name: `Get User By ID`
- Method: **GET**
- URL: `{{base_url}}/users/1/`
- (Replace `1` with actual user ID)

### Request 4: Toggle Theme
- Name: `Toggle Theme`
- Method: **POST**
- URL: `{{base_url}}/users/toggle_theme/`
- No body needed

---

## 📁 FOLDER 2: ORGANIZATIONS

### Request 1: Get My Organization
- Name: `Get My Organization`
- Method: **GET**
- URL: `{{base_url}}/organizations/`

### Request 2: List Departments
- Name: `List Departments`
- Method: **GET**
- URL: `{{base_url}}/departments/`

### Request 3: Create Department
- Name: `Create Department`
- Method: **POST**
- URL: `{{base_url}}/departments/`
- Body: **raw** → **JSON**
```json
{
  "name": "Engineering",
  "description": "Software development team"
}
```

### Request 4: List Teams
- Name: `List Teams`
- Method: **GET**
- URL: `{{base_url}}/teams/`

### Request 5: Create Team
- Name: `Create Team`
- Method: **POST**
- URL: `{{base_url}}/teams/`
- Body: **raw** → **JSON**
```json
{
  "name": "Frontend Team",
  "department": 1,
  "description": "UI/UX development"
}
```

---

## 📁 FOLDER 3: PROJECTS

### Request 1: List All Projects
- Name: `List All Projects`
- Method: **GET**
- URL: `{{base_url}}/projects/`

### Request 2: Create Project
- Name: `Create Project`
- Method: **POST**
- URL: `{{base_url}}/projects/`
- Body: **raw** → **JSON**
```json
{
  "name": "Mobile App Development",
  "description": "Build iOS and Android apps",
  "partner_organization": null,
  "members": []
}
```

### Request 3: Get Project Details
- Name: `Get Project Details`
- Method: **GET**
- URL: `{{base_url}}/projects/1/`
- (Replace `1` with actual project ID)

### Request 4: Update Project
- Name: `Update Project`
- Method: **PUT**
- URL: `{{base_url}}/projects/1/`
- Body: **raw** → **JSON**
```json
{
  "name": "Mobile App - Updated",
  "description": "Updated description",
  "status": "ACTIVE"
}
```

### Request 5: Get Project Analytics (Premium Feature)
- Name: `Get Project Analytics`
- Method: **GET**
- URL: `{{base_url}}/projects/1/analytics/`

### Request 6: Delete Project
- Name: `Delete Project`
- Method: **DELETE**
- URL: `{{base_url}}/projects/1/`

---

## 📁 FOLDER 4: CHANNELS

### Request 1: List All Channels
- Name: `List All Channels`
- Method: **GET**
- URL: `{{base_url}}/channels/`

### Request 2: Create Channel
- Name: `Create Channel`
- Method: **POST**
- URL: `{{base_url}}/channels/`
- Body: **raw** → **JSON**
```json
{
  "name": "general",
  "description": "General discussion",
  "channel_type": "PROJECT",
  "shared_project": 1,
  "members": []
}
```

### Request 3: Get Channel Details
- Name: `Get Channel Details`
- Method: **GET**
- URL: `{{base_url}}/channels/1/`

### Request 4: Get Channel Messages
- Name: `Get Channel Messages`
- Method: **GET**
- URL: `{{base_url}}/channels/1/messages/`

### Request 5: Update Channel
- Name: `Update Channel`
- Method: **PUT**
- URL: `{{base_url}}/channels/1/`
- Body: **raw** → **JSON**
```json
{
  "name": "general-updated",
  "description": "Updated description"
}
```

### Request 6: Delete Channel
- Name: `Delete Channel`
- Method: **DELETE**
- URL: `{{base_url}}/channels/1/`

---

## 📁 FOLDER 5: MESSAGES

### Request 1: List All Messages
- Name: `List All Messages`
- Method: **GET**
- URL: `{{base_url}}/messages/`

### Request 2: Send Text Message
- Name: `Send Text Message`
- Method: **POST**
- URL: `{{base_url}}/messages/`
- Body: **raw** → **JSON**
```json
{
  "channel": 1,
  "content": "Hello team! This is a test message from Postman 🚀"
}
```

### Request 3: Send File Message
- Name: `Send File Message`
- Method: **POST**
- URL: `{{base_url}}/messages/`
- Body: **form-data**
  - `channel`: `1`
  - `content`: `Check out this document`
  - `file`: [Select file from your computer]

### Request 4: Get Message Details
- Name: `Get Message Details`
- Method: **GET**
- URL: `{{base_url}}/messages/1/`

### Request 5: Pin Message
- Name: `Pin Message`
- Method: **POST**
- URL: `{{base_url}}/messages/1/pin/`

### Request 6: Star Message
- Name: `Star Message`
- Method: **POST**
- URL: `{{base_url}}/messages/1/star/`

### Request 7: Reply to Message
- Name: `Reply to Message`
- Method: **POST**
- URL: `{{base_url}}/messages/1/reply/`
- Body: **raw** → **JSON**
```json
{
  "content": "This is a reply to your message"
}
```

### Request 8: Forward Message
- Name: `Forward Message`
- Method: **POST**
- URL: `{{base_url}}/messages/1/forward/`
- Body: **raw** → **JSON**
```json
{
  "target_channel_id": 2
}
```

### Request 9: Create Task from Message
- Name: `Create Task from Message`
- Method: **POST**
- URL: `{{base_url}}/messages/1/create_task/`

### Request 10: Create Meeting from Message
- Name: `Create Meeting from Message`
- Method: **POST**
- URL: `{{base_url}}/messages/1/create_meeting/`
- Body: **raw** → **JSON**
```json
{
  "title": "Project Review Meeting"
}
```

### Request 11: Add Message Files to Project
- Name: `Add to Project Files`
- Method: **POST**
- URL: `{{base_url}}/messages/1/add_to_files/`

### Request 12: Link Message to Milestone
- Name: `Link to Milestone`
- Method: **POST**
- URL: `{{base_url}}/messages/1/link_milestone/`
- Body: **raw** → **JSON**
```json
{
  "milestone_id": 1
}
```

### Request 13: Delete Message
- Name: `Delete Message`
- Method: **DELETE**
- URL: `{{base_url}}/messages/1/`

---

## 📁 FOLDER 6: SUPPORT TICKETS

### Request 1: List All Tickets
- Name: `List All Tickets`
- Method: **GET**
- URL: `{{base_url}}/tickets/`

### Request 2: Create Ticket
- Name: `Create Support Ticket`
- Method: **POST**
- URL: `{{base_url}}/tickets/`
- Body: **raw** → **JSON**
```json
{
  "subject": "Cannot upload files",
  "description": "Getting error when trying to upload PDF files",
  "priority": "HIGH",
  "category": "TECHNICAL"
}
```

### Request 3: Get Ticket Details
- Name: `Get Ticket Details`
- Method: **GET**
- URL: `{{base_url}}/tickets/1/`

### Request 4: Add Message to Ticket
- Name: `Add Ticket Message`
- Method: **POST**
- URL: `{{base_url}}/tickets/1/add_message/`
- Body: **raw** → **JSON**
```json
{
  "message": "I tried clearing cache but issue still persists"
}
```

### Request 5: Update Ticket
- Name: `Update Ticket`
- Method: **PUT**
- URL: `{{base_url}}/tickets/1/`
- Body: **raw** → **JSON**
```json
{
  "status": "RESOLVED",
  "priority": "LOW"
}
```

### Request 6: List Ticket Messages
- Name: `List Ticket Messages`
- Method: **GET**
- URL: `{{base_url}}/ticket-messages/?ticket=1`

---

## 🎯 STEP 4: TEST YOUR API

### Run Single Request
1. Click on any request
2. Click **"Send"** button
3. See response below

### Run All Requests (Collection Runner)
1. Click on collection name
2. Click **"Run"** button (top right)
3. Click **"Run ConnectFlow API"**
4. Watch all requests execute automatically

---

## 🎯 STEP 5: PRESENT YOUR API

### During Presentation:

**1. Show Authentication**
- Open "Get My Profile" request
- Explain: "All requests use Firebase Bearer token authentication"
- Click Send → Show your user data

**2. Show CRUD Operations**
- **CREATE**: Create Department or Project
- **READ**: List Projects or Channels
- **UPDATE**: Update a Project
- **DELETE**: Delete a Message

**3. Show Advanced Features**
- Pin/Star messages
- Reply/Forward messages
- Create task from message
- Project analytics (premium)
- Support tickets

**4. Show Real-time Features**
- Send a message via Postman
- Show it appears in your app immediately (WebSocket)

**5. Export Collection**
- Collection → ... → Export
- Share the JSON file with your audience

---

## 🚀 QUICK DEMO FLOW (5 MINUTES)

1. **GET** `/users/me/` - "Here's my authenticated user"
2. **GET** `/projects/` - "Here are all my projects"
3. **POST** `/projects/` - "Let's create a new project"
4. **GET** `/channels/` - "Here are the communication channels"
5. **POST** `/messages/` - "Send a message to a channel"
6. **POST** `/messages/1/pin/` - "Pin important messages"
7. **POST** `/tickets/` - "Create a support ticket"
8. **GET** `/projects/1/analytics/` - "Premium analytics feature"

---

## ❓ TROUBLESHOOTING

### Error: 401 Unauthorized
- Your token expired (valid for 1 hour)
- Get a new token from Step 1
- Update `token` in environment variables

### Error: 404 Not Found
- Check the ID in URL exists
- Check `base_url` is correct

### Error: 403 Forbidden
- You don't have permission for this resource
- Check if it's a premium feature
- Check if you're in the right organization

### Error: 500 Server Error
- Check your JSON syntax
- Check required fields are included
- Check server logs

---

## ✅ FINAL CHECKLIST

- [ ] Postman installed
- [ ] Environment created with base_url and token
- [ ] Collection created with Bearer auth
- [ ] All 6 folders created
- [ ] Tested at least one request from each folder
- [ ] Saved example responses
- [ ] Ready to present!

---

**THAT'S IT! You're ready to present your API. 🎉**
