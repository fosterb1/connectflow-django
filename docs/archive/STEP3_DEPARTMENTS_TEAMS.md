# Step 3: Departments & Teams System ✅

## What We Built

### 1. **Database Models**

#### Department Model
- Represents organizational departments (Engineering, Sales, Marketing, etc.)
- Fields:
  - `name` - Department name
  - `description` - Department description
  - `organization` - Link to organization
  - `head` - Department head (user with DEPT_HEAD role)
  - `is_active` - Active/inactive status
- **Relationships:**
  - Belongs to one Organization
  - Has many Teams
  - Has one Department Head
- **Properties:**
  - `member_count` - Total members across all teams

#### Team Model
- Represents teams within departments
- Fields:
  - `name` - Team name
  - `description` - Team description
  - `department` - Link to department
  - `manager` - Team manager (user with TEAM_MANAGER or DEPT_HEAD role)
  - `members` - Many-to-many relationship with users
  - `is_active` - Active/inactive status
- **Relationships:**
  - Belongs to one Department
  - Has one Manager
  - Has many Members
- **Properties:**
  - `member_count` - Number of team members
  - `organization` - Access organization through department

### 2. **Forms** (`apps/organizations/forms.py`)
- **DepartmentForm**: Create/edit departments with role-based user filtering
- **TeamForm**: Create/edit teams with intelligent member selection

### 3. **Views** (`apps/organizations/views.py`)
- **organization_overview**: Main organization structure view
- **department_list**: List all departments
- **department_create**: Create new department (Super Admin only)
- **department_edit**: Edit department (Admin or Dept Head)
- **department_delete**: Delete department (Super Admin only)
- **team_list**: List teams (optionally filtered by department)
- **team_create**: Create team (Admin or Managers)
- **team_edit**: Edit team (Admin, Dept Head, or Team Manager)
- **team_delete**: Delete team (Admin or Dept Head)

### 4. **Permission System**
Built-in role-based permissions:
- **Super Admin**: Full access to everything
- **Department Head**: Manage their department and teams
- **Team Manager**: Manage their team
- **Team Member**: View only

### 5. **Templates**
- `overview.html` - Organization structure with stats
- `department_list.html` - Grid view of departments
- `department_form.html` - Create/edit department
- `department_confirm_delete.html` - Delete confirmation
- `team_list.html` - Grid view of teams with member avatars
- `team_form.html` - Create/edit team with multi-select members
- `team_confirm_delete.html` - Delete confirmation

### 6. **Admin Interface**
Enhanced admin panels for:
- Departments: Shows member count, teams, and head
- Teams: Shows members with horizontal filter widget

---

## How to Test

### 1. Start the Server
```bash
cd C:\Users\foste\OneDrive\Desktop\connectflow-django
python manage.py runserver
```

### 2. Login as Admin
1. Go to **http://127.0.0.1:8000/**
2. Login: `admin` / `admin123`

### 3. View Organization Structure
1. Click "Organization" in the navigation
2. You'll see the overview with stats (currently 0 departments)

### 4. Create a Department
1. Click "+ New Department" button
2. Fill in:
   - **Name**: Engineering
   - **Description**: Software development team
   - **Department Head**: Select a user (or leave empty)
   - **Active**: Checked
3. Click "Create Department"
4. Success! You'll see it in the department list

### 5. Create Teams
1. From the department card, click "Add Team"
2. Fill in:
   - **Name**: Backend Team
   - **Description**: API and database development
   - **Manager**: Select a team manager
   - **Members**: Select multiple team members (hold Ctrl/Cmd)
   - **Active**: Checked
3. Click "Create Team"

### 6. View Teams
1. Click "View Teams" on any department
2. See all teams with:
   - Member count
   - Team manager
   - Member avatars (first 4 shown)

### 7. Edit & Delete
- Click "Edit" on any department/team
- Update information
- Or click "Delete this department/team" at the bottom

---

## Key Django Concepts Learned

### 1. **Foreign Key Relationships**
```python
department = models.ForeignKey(
    Department,
    on_delete=models.CASCADE,  # Delete teams when department is deleted
    related_name='teams'       # Access via department.teams.all()
)
```

**Explanation:**
- ForeignKey = "belongs to" relationship
- `on_delete=CASCADE` = automatic deletion of related objects
- `related_name` = reverse lookup from parent

### 2. **Many-to-Many Relationships**
```python
members = models.ManyToManyField(
    'accounts.User',
    related_name='teams',  # Access via user.teams.all()
    blank=True
)
```

**Explanation:**
- ManyToMany = many users can be in many teams
- Django creates a join table automatically
- Can query both directions: `team.members.all()` or `user.teams.all()`

### 3. **UUID Primary Keys**
```python
id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False
)
```

**Why UUID?**
- Globally unique (no collisions)
- Harder to guess than sequential IDs
- Better for distributed systems

### 4. **Model Properties**
```python
@property
def member_count(self):
    return self.members.count()
```

**Explanation:**
- Computed values, not stored in database
- Access like a field: `team.member_count`
- Useful for calculated data

### 5. **Query Optimization**
```python
departments = Department.objects.filter(
    organization=user.organization
).prefetch_related('teams')  # Reduces database queries
```

**Explanation:**
- `select_related` for ForeignKey (joins tables)
- `prefetch_related` for ManyToMany (separate query)
- Prevents N+1 query problem

### 6. **Form Customization**
```python
def __init__(self, *args, department=None, **kwargs):
    super().__init__(*args, **kwargs)
    if department:
        self.fields['manager'].queryset = User.objects.filter(
            organization=department.organization
        )
```

**Explanation:**
- Dynamic form field filtering
- Only show relevant users based on context
- Improves user experience

---

## File Structure

```
connectflow-django/
├── apps/
│   └── organizations/
│       ├── models.py                    ✅ UPDATED: Added Department & Team
│       ├── admin.py                     ✅ UPDATED: Added admin interfaces
│       ├── forms.py                     ✅ NEW: Department & Team forms
│       ├── views.py                     ✅ NEW: CRUD views
│       ├── urls.py                      ✅ NEW: URL routing
│       └── migrations/
│           └── 0002_department_team.py  ✅ NEW: Database migration
├── templates/
│   └── organizations/                   ✅ NEW: Organization templates
│       ├── overview.html
│       ├── department_list.html
│       ├── department_form.html
│       ├── department_confirm_delete.html
│       ├── team_list.html
│       ├── team_form.html
│       └── team_confirm_delete.html
└── connectflow/
    └── urls.py                          ✅ UPDATED: Added organizations URLs
```

---

## Database Schema

```
Organization (1) ──< Department (N)
                        │
                        └──< Team (N) >──< User (N)
                                             │
                                             └── (members)
```

**Relationships:**
- One Organization has Many Departments
- One Department has Many Teams
- One Team has Many Members (Users)
- One User can be in Many Teams

---

## API Endpoints

```
GET  /organization/                         # Overview
GET  /organization/departments/             # List departments
GET  /organization/departments/create/      # Create form
POST /organization/departments/create/      # Create action
GET  /organization/departments/{id}/edit/   # Edit form
POST /organization/departments/{id}/edit/   # Update action
POST /organization/departments/{id}/delete/ # Delete action

GET  /organization/teams/                              # All teams
GET  /organization/departments/{dept_id}/teams/        # Teams by dept
GET  /organization/departments/{dept_id}/teams/create/ # Create form
POST /organization/departments/{dept_id}/teams/create/ # Create action
GET  /organization/teams/{id}/edit/                    # Edit form
POST /organization/teams/{id}/edit/                    # Update action
POST /organization/teams/{id}/delete/                  # Delete action
```

---

## What's Next?

**Step 4: Channels System**
We'll build:
- **Channel Model** - Communication channels
- **Channel Types** - Official, Department, Team, Project, Private
- **Channel Permissions** - Role-based access control
- **Channel Views** - CRUD operations
- **Channel Sidebar** - Navigation for channels

This will set the foundation for real-time messaging!

---

## Troubleshooting

### Issue: "No departments showing"
**Solution**: Make sure you're logged in and your user has an organization assigned.

### Issue: "Can't create department"
**Solution**: Only Super Admins can create departments. Check your user role in admin panel.

### Issue: "Members dropdown is empty"
**Solution**: Users must be in the same organization to appear in the team members list.

### Issue: "Foreign Key constraint failed"
**Solution**: Make sure the department exists before creating a team.

---

## Testing Checklist

- [ ] Create a department as Super Admin
- [ ] Assign a department head
- [ ] Create a team within the department
- [ ] Add team members
- [ ] Assign a team manager
- [ ] View organization overview
- [ ] Edit a department
- [ ] Edit a team
- [ ] Delete a team
- [ ] Try creating department as regular user (should fail)
- [ ] View teams by department
- [ ] Check member avatars display correctly

---

**Date Completed**: December 14, 2024  
**Status**: ✅ Departments & Teams Complete - Ready for Step 4!
