# 🚀 Corporate Tools - Quick Implementation Guide

## 📋 Overview

This guide provides step-by-step instructions for implementing the Corporate Tools suite in ConnectFlow Pro. The tools will be organized under a unified navigation menu alongside the existing Performance module.

---

## 🏗️ Step 1: Create App Structure

### 1.1 Create the Tools App

```bash
# From project root
cd apps
mkdir -p tools/forms
mkdir -p tools/documents
mkdir -p tools/announcements
mkdir -p tools/bookings
mkdir -p tools/timeoff
```

### 1.2 Create Initial Files

```bash
# Create __init__.py files
touch tools/__init__.py
touch tools/forms/__init__.py
touch tools/documents/__init__.py
touch tools/announcements/__init__.py
touch tools/bookings/__init__.py
touch tools/timeoff/__init__.py

# Create core files
touch tools/forms/models.py
touch tools/forms/views.py
touch tools/forms/urls.py
touch tools/forms/admin.py
touch tools/forms/utils.py
```

---

## 📊 Step 2: Implement Forms Module (Priority 1)

### 2.1 Create Models

**File: `apps/tools/forms/models.py`**

```python
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import secrets

class Form(models.Model):
    """Custom form/survey created by users"""
    
    class FormType(models.TextChoices):
        SURVEY = 'SURVEY', _('Survey')
        FEEDBACK = 'FEEDBACK', _('Feedback Form')
        REGISTRATION = 'REGISTRATION', _('Event Registration')
        REQUEST = 'REQUEST', _('Service Request')
        ASSESSMENT = 'ASSESSMENT', _('Assessment')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='forms',
        db_index=True
    )
    
    # Basic Info
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    form_type = models.CharField(
        max_length=20,
        choices=FormType.choices,
        default=FormType.SURVEY
    )
    
    # Sharing & Access
    share_link = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text=_("Unique short URL for sharing")
    )
    is_public = models.BooleanField(
        default=False,
        help_text=_("Allow external access without login")
    )
    allow_anonymous = models.BooleanField(
        default=False,
        help_text=_("Allow anonymous responses")
    )
    require_login = models.BooleanField(
        default=True,
        help_text=_("Require user login to submit")
    )
    
    # Settings
    is_active = models.BooleanField(default=True, db_index=True)
    accepts_responses = models.BooleanField(default=True)
    max_responses = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("Maximum number of responses (blank = unlimited)")
    )
    closes_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Auto-close form at this date/time")
    )
    
    # Notifications
    send_email_on_submit = models.BooleanField(default=False)
    notification_emails = models.TextField(
        blank=True,
        help_text=_("Comma-separated email addresses")
    )
    
    # Audit
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='created_forms'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'forms'
        verbose_name = _('Form')
        verbose_name_plural = _('Forms')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['created_by', '-created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Generate share link if not exists
        if not self.share_link:
            self.share_link = secrets.token_urlsafe(12)
        super().save(*args, **kwargs)
    
    @property
    def response_count(self):
        return self.responses.count()
    
    @property
    def is_accepting_responses(self):
        if not self.accepts_responses or not self.is_active:
            return False
        if self.closes_at and timezone.now() > self.closes_at:
            return False
        if self.max_responses and self.response_count >= self.max_responses:
            return False
        return True


class FormField(models.Model):
    """Individual field within a form"""
    
    class FieldType(models.TextChoices):
        SHORT_TEXT = 'SHORT_TEXT', _('Short Text')
        LONG_TEXT = 'LONG_TEXT', _('Long Text (Paragraph)')
        MULTIPLE_CHOICE = 'MULTIPLE_CHOICE', _('Multiple Choice')
        CHECKBOXES = 'CHECKBOXES', _('Checkboxes')
        DROPDOWN = 'DROPDOWN', _('Dropdown')
        NUMBER = 'NUMBER', _('Number')
        DATE = 'DATE', _('Date')
        TIME = 'TIME', _('Time')
        EMAIL = 'EMAIL', _('Email')
        PHONE = 'PHONE', _('Phone')
        FILE = 'FILE', _('File Upload')
        RATING = 'RATING', _('Rating (Stars)')
        SCALE = 'SCALE', _('Linear Scale')
        SECTION = 'SECTION', _('Section Header')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name='fields'
    )
    
    # Field Configuration
    label = models.CharField(max_length=300)
    field_type = models.CharField(
        max_length=20,
        choices=FieldType.choices,
        default=FieldType.SHORT_TEXT
    )
    is_required = models.BooleanField(default=False)
    placeholder = models.CharField(max_length=200, blank=True)
    help_text = models.CharField(max_length=500, blank=True)
    
    # Options for choice-based fields (MULTIPLE_CHOICE, CHECKBOXES, DROPDOWN)
    options = models.JSONField(
        default=list,
        blank=True,
        help_text=_('List of options: ["Option 1", "Option 2"]')
    )
    
    # Validation Rules
    min_value = models.IntegerField(null=True, blank=True)
    max_value = models.IntegerField(null=True, blank=True)
    max_length = models.IntegerField(null=True, blank=True)
    pattern = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Regex pattern for validation")
    )
    
    # Conditional Logic
    show_if_field = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dependent_fields',
        help_text=_("Show this field only if another field has specific value")
    )
    show_if_value = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Value that triggers display")
    )
    
    # Ordering
    order = models.IntegerField(default=0, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'form_fields'
        verbose_name = _('Form Field')
        verbose_name_plural = _('Form Fields')
        ordering = ['order']
        indexes = [
            models.Index(fields=['form', 'order']),
        ]
    
    def __str__(self):
        return f"{self.form.title} - {self.label}"


class FormResponse(models.Model):
    """A submitted response to a form"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    
    # Respondent Information
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='form_responses'
    )
    is_anonymous = models.BooleanField(default=False)
    respondent_email = models.EmailField(
        blank=True,
        help_text=_("Email for external/anonymous respondents")
    )
    
    # Response Data
    answers = models.JSONField(
        default=dict,
        help_text=_('Field answers: {field_id: value}')
    )
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'form_responses'
        verbose_name = _('Form Response')
        verbose_name_plural = _('Form Responses')
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['form', '-submitted_at']),
            models.Index(fields=['user', '-submitted_at']),
        ]
    
    def __str__(self):
        if self.user:
            return f"{self.form.title} - {self.user.get_full_name()}"
        return f"{self.form.title} - Anonymous"
    
    @property
    def respondent_name(self):
        if self.is_anonymous:
            return "Anonymous"
        if self.user:
            return self.user.get_full_name() or self.user.username
        return self.respondent_email or "Unknown"
```

### 2.2 Create Views

**File: `apps/tools/forms/views.py`**

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Count, Q
from django.utils import timezone
from .models import Form, FormField, FormResponse
from apps.organizations.models import Organization
import json

# ============================================
# FORM MANAGEMENT VIEWS (Managers/Creators)
# ============================================

@login_required
def form_list(request):
    """List all forms created by user or their organization"""
    user = request.user
    
    # Forms created by user
    my_forms = Form.objects.filter(created_by=user)
    
    # Organization-wide forms (if manager/admin)
    org_forms = Form.objects.filter(
        organization=user.organization
    ).exclude(created_by=user)
    
    context = {
        'my_forms': my_forms,
        'org_forms': org_forms,
    }
    return render(request, 'tools/forms/form_list.html', context)


@login_required
def form_create(request):
    """Create a new form"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        form_type = request.POST.get('form_type', 'SURVEY')
        
        form = Form.objects.create(
            organization=request.user.organization,
            title=title,
            description=description,
            form_type=form_type,
            created_by=request.user
        )
        
        messages.success(request, f'Form "{title}" created successfully!')
        return redirect('tools:forms:form_edit', form_id=form.id)
    
    return render(request, 'tools/forms/form_create.html')


@login_required
def form_edit(request, form_id):
    """Edit form settings and fields (Builder UI)"""
    form = get_object_or_404(Form, id=form_id)
    
    # Permission check
    if form.created_by != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("You don't have permission to edit this form.")
    
    if request.method == 'POST':
        # Update form settings
        form.title = request.POST.get('title', form.title)
        form.description = request.POST.get('description', form.description)
        form.is_public = request.POST.get('is_public') == 'on'
        form.allow_anonymous = request.POST.get('allow_anonymous') == 'on'
        form.send_email_on_submit = request.POST.get('send_email_on_submit') == 'on'
        form.notification_emails = request.POST.get('notification_emails', '')
        
        form.save()
        messages.success(request, 'Form settings updated!')
        return redirect('tools:forms:form_edit', form_id=form.id)
    
    context = {
        'form': form,
        'fields': form.fields.all(),
        'share_url': request.build_absolute_uri(f'/f/{form.share_link}/'),
    }
    return render(request, 'tools/forms/form_edit.html', context)


@login_required
def form_field_add(request, form_id):
    """Add a field to the form (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    form = get_object_or_404(Form, id=form_id)
    
    # Permission check
    if form.created_by != request.user and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    data = json.loads(request.body)
    
    # Get current max order
    max_order = form.fields.aggregate(models.Max('order'))['order__max'] or 0
    
    field = FormField.objects.create(
        form=form,
        label=data.get('label', 'Untitled Question'),
        field_type=data.get('field_type', 'SHORT_TEXT'),
        is_required=data.get('is_required', False),
        order=max_order + 1
    )
    
    return JsonResponse({
        'id': str(field.id),
        'label': field.label,
        'field_type': field.field_type,
        'order': field.order
    })


@login_required
def form_responses(request, form_id):
    """View all responses to a form"""
    form = get_object_or_404(Form, id=form_id)
    
    # Permission check
    if form.created_by != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("You don't have permission to view responses.")
    
    responses = form.responses.all().select_related('user')
    
    context = {
        'form': form,
        'responses': responses,
        'total_responses': responses.count(),
    }
    return render(request, 'tools/forms/form_responses.html', context)


@login_required
def form_analytics(request, form_id):
    """Show analytics and charts for form responses"""
    form = get_object_or_404(Form, id=form_id)
    
    # Permission check
    if form.created_by != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("You don't have permission to view analytics.")
    
    responses = form.responses.all()
    
    # Aggregate data for each field
    field_stats = []
    for field in form.fields.all():
        if field.field_type == FormField.FieldType.SECTION:
            continue
        
        # Extract all answers for this field
        answers = []
        for response in responses:
            answer = response.answers.get(str(field.id))
            if answer:
                answers.append(answer)
        
        # Calculate statistics based on field type
        stats = {
            'field': field,
            'total_responses': len(answers),
        }
        
        if field.field_type in ['MULTIPLE_CHOICE', 'DROPDOWN']:
            # Count each option
            from collections import Counter
            counts = Counter(answers)
            stats['options'] = [
                {'label': k, 'count': v, 'percentage': (v/len(answers)*100) if answers else 0}
                for k, v in counts.items()
            ]
        
        elif field.field_type == 'RATING':
            # Average rating
            ratings = [int(r) for r in answers if r]
            stats['average'] = sum(ratings) / len(ratings) if ratings else 0
            stats['distribution'] = Counter(ratings)
        
        elif field.field_type == 'NUMBER':
            # Min, max, average
            numbers = [float(n) for n in answers if n]
            stats['min'] = min(numbers) if numbers else 0
            stats['max'] = max(numbers) if numbers else 0
            stats['average'] = sum(numbers) / len(numbers) if numbers else 0
        
        field_stats.append(stats)
    
    context = {
        'form': form,
        'total_responses': responses.count(),
        'field_stats': field_stats,
    }
    return render(request, 'tools/forms/form_analytics.html', context)


# ============================================
# PUBLIC FORM SUBMISSION VIEWS
# ============================================

def form_submit_page(request, share_link):
    """Public page for submitting a form"""
    form = get_object_or_404(Form, share_link=share_link)
    
    # Check if form is accepting responses
    if not form.is_accepting_responses:
        return render(request, 'tools/forms/form_closed.html', {'form': form})
    
    # Check login requirement
    if form.require_login and not request.user.is_authenticated:
        messages.warning(request, 'Please login to submit this form.')
        return redirect('accounts:login')
    
    if request.method == 'POST':
        # Collect answers
        answers = {}
        for field in form.fields.all():
            if field.field_type == FormField.FieldType.SECTION:
                continue
            
            field_name = f'field_{field.id}'
            answer = request.POST.get(field_name)
            
            # Validation
            if field.is_required and not answer:
                messages.error(request, f'{field.label} is required.')
                return redirect('tools:forms:submit', share_link=share_link)
            
            if answer:
                answers[str(field.id)] = answer
        
        # Create response
        response = FormResponse.objects.create(
            form=form,
            user=request.user if request.user.is_authenticated else None,
            is_anonymous=form.allow_anonymous,
            answers=answers,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Send notification email if enabled
        if form.send_email_on_submit and form.notification_emails:
            # TODO: Send email using Django's send_mail
            pass
        
        messages.success(request, 'Your response has been submitted!')
        return redirect('tools:forms:submit_success', share_link=share_link)
    
    context = {
        'form': form,
        'fields': form.fields.all(),
    }
    return render(request, 'tools/forms/form_submit.html', context)


def form_submit_success(request, share_link):
    """Thank you page after submission"""
    form = get_object_or_404(Form, share_link=share_link)
    return render(request, 'tools/forms/form_success.html', {'form': form})
```

### 2.3 Create URL Configuration

**File: `apps/tools/forms/urls.py`**

```python
from django.urls import path
from . import views

app_name = 'forms'

urlpatterns = [
    # Management
    path('', views.form_list, name='form_list'),
    path('create/', views.form_create, name='form_create'),
    path('<uuid:form_id>/edit/', views.form_edit, name='form_edit'),
    path('<uuid:form_id>/responses/', views.form_responses, name='form_responses'),
    path('<uuid:form_id>/analytics/', views.form_analytics, name='form_analytics'),
    
    # AJAX endpoints
    path('<uuid:form_id>/field/add/', views.form_field_add, name='form_field_add'),
]
```

**File: `apps/tools/urls.py`** (Main tools router)

```python
from django.urls import path, include

app_name = 'tools'

urlpatterns = [
    path('forms/', include('apps.tools.forms.urls')),
    # Future: documents, announcements, etc.
]
```

---

## ⚙️ Step 3: Update Project Configuration

### 3.1 Update settings.py

```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... existing apps ...
    'apps.performance',
    'apps.tools.forms',  # NEW
]
```

### 3.2 Update main URLs

**File: `connectflow/urls.py`**

```python
urlpatterns = [
    # ... existing paths ...
    path('tools/', include('apps.tools.urls')),  # NEW
    
    # Public form submission (no /tools/ prefix)
    path('f/<str:share_link>/', 
         include('apps.tools.forms.public_urls')),  # NEW
]
```

**File: `apps/tools/forms/public_urls.py`**

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.form_submit_page, name='submit'),
    path('success/', views.form_submit_success, name='submit_success'),
]
```

---

## 🎨 Step 4: Create Templates

### 4.1 Base Tools Template

**File: `templates/tools/base.html`**

```html
{% extends "base.html" %}

{% block content %}
<div class="flex h-screen bg-gray-100">
    <!-- Sidebar Navigation -->
    <aside class="w-64 bg-white shadow-lg">
        <nav class="mt-5 px-4">
            <h2 class="text-gray-600 text-xs font-semibold uppercase tracking-wider mb-2">
                Corporate Tools
            </h2>
            <a href="{% url 'tools:forms:form_list' %}" 
               class="flex items-center px-4 py-2 text-gray-700 rounded hover:bg-gray-100">
                <span class="mr-3">📋</span>
                <span>Forms & Surveys</span>
            </a>
            <a href="{% url 'performance:my_dashboard' %}" 
               class="flex items-center px-4 py-2 text-gray-700 rounded hover:bg-gray-100">
                <span class="mr-3">📊</span>
                <span>Performance</span>
            </a>
            <!-- Future: Documents, Announcements, etc. -->
        </nav>
    </aside>
    
    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto p-8">
        {% block tool_content %}{% endblock %}
    </main>
</div>
{% endblock %}
```

### 4.2 Form List Template

**File: `templates/tools/forms/form_list.html`**

```html
{% extends "tools/base.html" %}

{% block tool_content %}
<div class="mb-6 flex justify-between items-center">
    <h1 class="text-3xl font-bold text-gray-900">Forms & Surveys</h1>
    <a href="{% url 'tools:forms:form_create' %}" 
       class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
        + Create Form
    </a>
</div>

<!-- My Forms -->
<div class="bg-white rounded-lg shadow mb-6">
    <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-lg font-semibold">My Forms</h2>
    </div>
    <div class="p-6">
        {% if my_forms %}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {% for form in my_forms %}
            <div class="border rounded-lg p-4 hover:shadow-lg transition">
                <h3 class="font-semibold text-lg mb-2">{{ form.title }}</h3>
                <p class="text-gray-600 text-sm mb-4">
                    {{ form.response_count }} responses
                </p>
                <div class="flex space-x-2">
                    <a href="{% url 'tools:forms:form_edit' form.id %}" 
                       class="text-blue-600 hover:underline text-sm">Edit</a>
                    <a href="{% url 'tools:forms:form_responses' form.id %}" 
                       class="text-green-600 hover:underline text-sm">Responses</a>
                    <a href="{% url 'tools:forms:form_analytics' form.id %}" 
                       class="text-purple-600 hover:underline text-sm">Analytics</a>
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <p class="text-gray-500">You haven't created any forms yet.</p>
        {% endif %}
    </div>
</div>

<!-- Organization Forms -->
{% if org_forms %}
<div class="bg-white rounded-lg shadow">
    <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-lg font-semibold">Organization Forms</h2>
    </div>
    <div class="p-6">
        <div class="space-y-2">
            {% for form in org_forms %}
            <div class="border-l-4 border-blue-500 pl-4 py-2">
                <h3 class="font-semibold">{{ form.title }}</h3>
                <p class="text-sm text-gray-600">
                    Created by {{ form.created_by.get_full_name }} • 
                    {{ form.response_count }} responses
                </p>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
{% endif %}
{% endblock %}
```

---

## 🗄️ Step 5: Run Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser if needed
python manage.py createsuperuser
```

---

## 🧪 Step 6: Testing

### 6.1 Create Test Data

**File: `apps/tools/forms/tests.py`**

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization
from .models import Form, FormField, FormResponse

User = get_user_model()

class FormModelTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Test Corp")
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            organization=self.org
        )
    
    def test_form_creation(self):
        """Test creating a form"""
        form = Form.objects.create(
            organization=self.org,
            title="Employee Survey",
            created_by=self.user
        )
        self.assertIsNotNone(form.share_link)
        self.assertEqual(form.title, "Employee Survey")
    
    def test_form_field_creation(self):
        """Test adding fields to a form"""
        form = Form.objects.create(
            organization=self.org,
            title="Test Form",
            created_by=self.user
        )
        field = FormField.objects.create(
            form=form,
            label="What's your name?",
            field_type=FormField.FieldType.SHORT_TEXT,
            is_required=True
        )
        self.assertEqual(form.fields.count(), 1)
        self.assertTrue(field.is_required)
    
    def test_form_response_submission(self):
        """Test submitting a response"""
        form = Form.objects.create(
            organization=self.org,
            title="Test Form",
            created_by=self.user
        )
        field = FormField.objects.create(
            form=form,
            label="Email",
            field_type=FormField.FieldType.EMAIL
        )
        
        response = FormResponse.objects.create(
            form=form,
            user=self.user,
            answers={str(field.id): "test@example.com"}
        )
        
        self.assertEqual(form.response_count, 1)
        self.assertEqual(response.respondent_name, self.user.get_full_name())
```

### 6.2 Run Tests

```bash
python manage.py test apps.tools.forms
```

---

## 📝 Step 7: Admin Interface

**File: `apps/tools/forms/admin.py`**

```python
from django.contrib import admin
from .models import Form, FormField, FormResponse

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ['title', 'form_type', 'organization', 'created_by', 
                   'response_count', 'is_active', 'created_at']
    list_filter = ['form_type', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['share_link', 'created_at', 'updated_at']
    
    def response_count(self, obj):
        return obj.response_count
    response_count.short_description = 'Responses'

@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    list_display = ['label', 'form', 'field_type', 'is_required', 'order']
    list_filter = ['field_type', 'is_required']
    search_fields = ['label', 'form__title']

@admin.register(FormResponse)
class FormResponseAdmin(admin.ModelAdmin):
    list_display = ['form', 'respondent_name', 'submitted_at']
    list_filter = ['form', 'submitted_at', 'is_anonymous']
    search_fields = ['form__title', 'user__username']
    readonly_fields = ['submitted_at']
```

---

## 🚀 Step 8: Deploy

### 8.1 Update Requirements

```bash
# Add to requirements.txt
# (No new dependencies needed for basic forms)
```

### 8.2 Deployment Checklist

- [ ] Run migrations on production database
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Test form creation and submission
- [ ] Verify share links work
- [ ] Check email notifications (if enabled)
- [ ] Test on mobile devices

---

## 📊 Step 9: Analytics & Monitoring

### Track these metrics:
- Number of forms created per week
- Average response rate
- Most popular form types
- User adoption rate

---

## 🎯 Next Steps

1. **Phase 2**: Add drag & drop field builder (SortableJS)
2. **Phase 3**: Implement Documents module
3. **Phase 4**: Build Announcements system
4. **Phase 5**: Create Resource Booking calendar
5. **Phase 6**: Add Time-Off management

---

## 🆘 Troubleshooting

### Issue: Share link not working
- Check URL configuration in main `urls.py`
- Verify `share_link` is generated on form save

### Issue: Responses not saving
- Check form's `is_accepting_responses` property
- Verify field validation rules

### Issue: Permission errors
- Check user's organization matches form's organization
- Verify creator permissions

---

**Ready to launch?** Start with `python manage.py runserver` and navigate to `/tools/forms/`! 🚀
