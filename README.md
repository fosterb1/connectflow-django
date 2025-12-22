# ConnectFlow Pro - Django Edition

A unified communication platform for organizational collaboration with hierarchical channels, breakout rooms, and real-time messaging.

## 📚 Documentation

**→ [View Complete Documentation Index](docs/INDEX.md)**

### Quick Links
- 🚀 [Cloudinary Setup Guide](docs/deployment/CLOUDINARY_COMPLETE_SETUP.md) - Essential for image storage
- 🔧 [Database vs File Storage](docs/deployment/DATABASE_VS_FILE_STORAGE.md) - Understanding the architecture
- 🐛 [Avatar Troubleshooting](AVATAR_TROUBLESHOOTING.md) - Fix image issues
- 📱 [Deployment Guide](docs/deployment/RENDER_DEPLOYMENT.md) - Deploy to Render.com

---

## 🎯 Project Overview

**ConnectFlow Pro** is a Django-based organizational communication system that enables structured communication across teams and departments with role-based access control.

## ✨ Core Features

### 1. **Multi-Tiered Organizational Structure**

- Role-based access: Super Admin, Department Head, Team Manager, Team Member
- Visual organizational chart
- Department & Team channels with automatic assignment
- Cross-functional project channels

### 2. **Intelligent Channel System**

- **Official Announcements**: Broadcast-only leadership communications
- **Department Channels**: Intra-department collaboration
- **Team Spaces**: Daily team collaboration
- **Project Rooms**: Time-bound initiative channels
- **Private Groups**: Sensitive discussions

### 3. **Dynamic Breakout Rooms**

- Create temporary discussion rooms from any channel
- Timer-based sessions with auto-return
- Selective participant invitations
- AI-powered summary generation

### 4. **Real-Time Messaging**

- Instant message delivery via WebSockets (Django Channels)
- Online presence indicators
- Typing indicators
- Read receipts
- Message reactions and replies

### 5. **File Sharing (Telegram-Style)**

- Multi-file upload (5-10 files at once)
- Drag & drop support
- Image preview and compression
- Progress tracking
- Inline image display
- Document handling (PDF, DOC, ZIP)

### 6. **Message Features**

- Copy, edit, delete messages
- Reply threading
- Emoji reactions
- User mentions with @ autocomplete
- Message search and filtering
- Voice messages

### 7. **Management & Analytics**

- Manager dashboard with team metrics
- Approval workflows
- Emergency broadcast system
- Compliance tools (message retention, export)

## 🛠️ Technology Stack

### Backend

- **Django 5.0+**: Web framework
- **Django REST Framework**: RESTful API (for mobile/external integrations)
- **Django Channels**: WebSocket support for real-time features
- **PostgreSQL**: Primary database
- **Redis**: Caching, sessions, and Channels layer
- **Celery**: Async task processing
- **django-storages + AWS S3**: File storage

### Frontend

- **Django Templates**: Server-side rendering with Jinja2 template engine
- **HTML5 + CSS3**: Modern semantic markup and styling
- **JavaScript (Vanilla/Alpine.js)**: Interactivity and dynamic features
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **WebSocket (JavaScript)**: Real-time client for Django Channels
- **HTMX** (optional): Modern interactions without heavy JavaScript

### Development Tools

- **pip + venv**: Dependency management and virtual environments
- **Black**: Code formatting
- **Flake8**: Linting
- **pytest**: Testing
- **Docker**: Containerization

## 📋 Requirements

### Functional Requirements

#### Authentication & Authorization

- User registration with organization codes
- Role-based permissions (RBAC)
- Session management
- Multi-device support

#### Communication

- Real-time message delivery
- Channel-based conversations
- Direct messages
- Breakout room management
- File attachments up to 10MB

#### Organization Management

- Create/manage departments and teams
- Assign users to roles
- Channel creation and permissions
- User directory and org chart

#### Notifications

- In-app notifications
- Email notifications
- Push notifications (future)

### Non-Functional Requirements

- **Performance**: Message delivery < 100ms
- **Scalability**: Support 1000+ concurrent users
- **Security**: Encrypted connections, secure file storage
- **Availability**: 99.9% uptime
- **Compliance**: Message retention policies

## 📁 Project Structure

```
connectflow-django/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── docker-compose.yml
├── connectflow/              # Main project config
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── celery.py
├── apps/
│   ├── accounts/             # User authentication & profiles
│   ├── organizations/        # Org structure & departments
│   ├── channels/             # Channel management
│   ├── messaging/            # Messages, files, reactions
│   ├── breakouts/            # Breakout room functionality
│   ├── notifications/        # Notification system
│   └── analytics/            # Analytics & reporting
├── templates/                # Django HTML templates
│   ├── base.html
│   ├── accounts/
│   ├── channels/
│   ├── messaging/
│   └── components/           # Reusable template components
├── static/                   # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── media/                    # Uploaded files
└── tests/                    # Test suite
```

## 🗃️ Database Models Overview

### Core Models

- **Organization**: Company/organization entity
- **User**: Extended Django user with roles
- **Department**: Organizational departments
- **Team**: Teams within departments
- **Channel**: Communication channels
- **Message**: Chat messages
- **BreakoutRoom**: Temporary discussion rooms
- **Attachment**: File uploads
- **Reaction**: Message reactions
- **Notification**: User notifications

## 🚀 Development Phases

### Phase 1: Foundation (Weeks 1-2)

- ✅ Project setup and configuration
- ✅ Django project initialization
- Database models (User, Organization, Department, Team)
- Basic authentication with Django templates
- Admin interface
- Base templates and layout

### Phase 2: Core Features (Weeks 3-4)

- Channel management with CRUD views
- Real-time messaging with Channels + WebSocket
- File upload system with forms
- Template-based UI for chat interface

### Phase 3: Advanced Features (Weeks 5-6)

- Breakout rooms with dynamic UI
- Message reactions and threading
- Search functionality with filters
- User mentions with autocomplete
- Django template tags for common components

### Phase 4: Management & Polish (Weeks 7-8)

- Analytics dashboard
- Approval workflows
- Testing and optimization
- Documentation

## 🔧 Installation (Coming Soon)

```bash
# Clone repository
git clone <repo-url>
cd connectflow-django

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## 📝 Environment Variables

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost/connectflow
REDIS_URL=redis://localhost:6379/0
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=apps
```

## 📚 API Documentation

API documentation will be available at `/api/docs/` using drf-spectacular or Swagger.

## 🤝 Contributing

This is a learning project. Follow Django best practices and PEP 8 style guide.

## 📄 License

[To be determined]

## 👨‍💻 Author

Built as a learning project to understand Django architecture and real-time web applications.

---

**Version**: 0.1.0  
**Status**: Initial Setup  
**Last Updated**: December 2025
