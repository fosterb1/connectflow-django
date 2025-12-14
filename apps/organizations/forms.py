from django import forms
from django.contrib.auth import get_user_model
from .models import Organization, Department, Team

User = get_user_model()


class DepartmentForm(forms.ModelForm):
    """Form for creating and editing departments."""
    
    class Meta:
        model = Department
        fields = ['name', 'description', 'head', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'e.g., Engineering, Sales, Marketing'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'Department description...',
                'rows': 3
            }),
            'head': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'
            })
        }
    
    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter department heads to only show users from the same organization with DEPT_HEAD role
        if organization:
            self.fields['head'].queryset = User.objects.filter(
                organization=organization,
                role=User.Role.DEPT_HEAD
            )
        else:
            self.fields['head'].queryset = User.objects.filter(role=User.Role.DEPT_HEAD)
        
        # Make head field optional
        self.fields['head'].required = False


class TeamForm(forms.ModelForm):
    """Form for creating and editing teams."""
    
    class Meta:
        model = Team
        fields = ['name', 'description', 'manager', 'members', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'e.g., Backend Team, Sales Team A'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'Team description...',
                'rows': 3
            }),
            'manager': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
            }),
            'members': forms.SelectMultiple(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'size': '5'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'
            })
        }
    
    def __init__(self, *args, department=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter managers and members based on department's organization
        if department:
            organization = department.organization
            
            # Managers can be TEAM_MANAGER or DEPT_HEAD from same organization
            self.fields['manager'].queryset = User.objects.filter(
                organization=organization,
                role__in=[User.Role.TEAM_MANAGER, User.Role.DEPT_HEAD]
            )
            
            # Members can be any user from the same organization
            self.fields['members'].queryset = User.objects.filter(
                organization=organization
            )
        else:
            self.fields['manager'].queryset = User.objects.filter(
                role__in=[User.Role.TEAM_MANAGER, User.Role.DEPT_HEAD]
            )
            self.fields['members'].queryset = User.objects.all()
        
        # Make fields optional
        self.fields['manager'].required = False
        self.fields['members'].required = False
