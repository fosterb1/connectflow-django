from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .models import Organization, Department, Team
from .forms import DepartmentForm, TeamForm


@login_required
def organization_overview(request):
    """Display organization structure overview."""
    user = request.user
    
    if not user.organization:
        messages.warning(request, 'You are not assigned to any organization.')
        return redirect('accounts:dashboard')
    
    departments = Department.objects.filter(
        organization=user.organization
    ).prefetch_related('teams').annotate(
        team_count=Count('teams')
    )
    
    context = {
        'organization': user.organization,
        'departments': departments,
    }
    return render(request, 'organizations/overview.html', context)


@login_required
def department_list(request):
    """List all departments in user's organization."""
    user = request.user
    
    if not user.organization:
        messages.warning(request, 'You are not assigned to any organization.')
        return redirect('accounts:dashboard')
    
    departments = Department.objects.filter(
        organization=user.organization
    ).select_related('head', 'organization').annotate(
        team_count=Count('teams')
    )
    
    context = {
        'departments': departments,
        'can_manage': user.is_admin or user.role == user.Role.DEPT_HEAD
    }
    return render(request, 'organizations/department_list.html', context)


@login_required
def department_create(request):
    """Create a new department."""
    user = request.user
    
    # Only super admins can create departments
    if not user.is_admin:
        messages.error(request, 'You do not have permission to create departments.')
        return redirect('organizations:department_list')
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, organization=user.organization)
        if form.is_valid():
            department = form.save(commit=False)
            department.organization = user.organization
            department.save()
            messages.success(request, f'Department "{department.name}" created successfully!')
            return redirect('organizations:department_list')
    else:
        form = DepartmentForm(organization=user.organization)
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'organizations/department_form.html', context)


@login_required
def department_edit(request, pk):
    """Edit an existing department."""
    user = request.user
    department = get_object_or_404(Department, pk=pk, organization=user.organization)
    
    # Only super admins or department heads can edit
    if not (user.is_admin or department.head == user):
        messages.error(request, 'You do not have permission to edit this department.')
        return redirect('organizations:department_list')
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department, organization=user.organization)
        if form.is_valid():
            form.save()
            messages.success(request, f'Department "{department.name}" updated successfully!')
            return redirect('organizations:department_list')
    else:
        form = DepartmentForm(instance=department, organization=user.organization)
    
    context = {'form': form, 'action': 'Edit', 'department': department}
    return render(request, 'organizations/department_form.html', context)


@login_required
def department_delete(request, pk):
    """Delete a department."""
    user = request.user
    department = get_object_or_404(Department, pk=pk, organization=user.organization)
    
    # Only super admins can delete departments
    if not user.is_admin:
        messages.error(request, 'You do not have permission to delete departments.')
        return redirect('organizations:department_list')
    
    if request.method == 'POST':
        department_name = department.name
        department.delete()
        messages.success(request, f'Department "{department_name}" deleted successfully!')
        return redirect('organizations:department_list')
    
    context = {'department': department}
    return render(request, 'organizations/department_confirm_delete.html', context)


@login_required
def team_list(request, department_pk=None):
    """List teams, optionally filtered by department."""
    user = request.user
    
    if not user.organization:
        messages.warning(request, 'You are not assigned to any organization.')
        return redirect('accounts:dashboard')
    
    teams = Team.objects.filter(
        department__organization=user.organization
    ).select_related('department', 'manager')
    
    if department_pk:
        department = get_object_or_404(Department, pk=department_pk, organization=user.organization)
        teams = teams.filter(department=department)
    else:
        department = None
    
    context = {
        'teams': teams,
        'department': department,
        'can_manage': user.is_admin or user.is_manager
    }
    return render(request, 'organizations/team_list.html', context)


@login_required
def team_create(request, department_pk):
    """Create a new team within a department."""
    user = request.user
    department = get_object_or_404(Department, pk=department_pk, organization=user.organization)
    
    # Only admins, department heads, and team managers can create teams
    if not (user.is_admin or user.is_manager):
        messages.error(request, 'You do not have permission to create teams.')
        return redirect('organizations:team_list', department_pk=department_pk)
    
    if request.method == 'POST':
        form = TeamForm(request.POST, department=department)
        if form.is_valid():
            team = form.save(commit=False)
            team.department = department
            team.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, f'Team "{team.name}" created successfully!')
            return redirect('organizations:department_team_list', department_pk=department_pk)
    else:
        form = TeamForm(department=department)
    
    context = {'form': form, 'action': 'Create', 'department': department}
    return render(request, 'organizations/team_form.html', context)


@login_required
def team_edit(request, pk):
    """Edit an existing team."""
    user = request.user
    team = get_object_or_404(Team, pk=pk, department__organization=user.organization)
    
    # Only admins, department heads, or team manager can edit
    if not (user.is_admin or team.department.head == user or team.manager == user):
        messages.error(request, 'You do not have permission to edit this team.')
        return redirect('organizations:team_list')
    
    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team, department=team.department)
        if form.is_valid():
            form.save()
            messages.success(request, f'Team "{team.name}" updated successfully!')
            return redirect('organizations:team_list', department_pk=team.department.pk)
    else:
        form = TeamForm(instance=team, department=team.department)
    
    context = {'form': form, 'action': 'Edit', 'team': team, 'department': team.department}
    return render(request, 'organizations/team_form.html', context)


@login_required
def team_delete(request, pk):
    """Delete a team."""
    user = request.user
    team = get_object_or_404(Team, pk=pk, department__organization=user.organization)
    
    # Only admins and department heads can delete teams
    if not (user.is_admin or team.department.head == user):
        messages.error(request, 'You do not have permission to delete teams.')
        return redirect('organizations:team_list')
    
    if request.method == 'POST':
        team_name = team.name
        department_pk = team.department.pk
        team.delete()
        messages.success(request, f'Team "{team_name}" deleted successfully!')
        return redirect('organizations:team_list_by_dept', department_pk=department_pk)
    
    context = {'team': team}
    return render(request, 'organizations/team_confirm_delete.html', context)
