from django.shortcuts import render, redirect, get_object_or_404
from .models import Account, Project, Task, Sprint
from .forms import ProjectForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
import json
from django.http import JsonResponse

# View to list the accounts owned by the logged-in user
def account_list(request):
    accounts = Account.objects.filter(owner=request.user)  # Get accounts where the logged-in user is the owner
    return render(request, 'account_list.html', {'accounts': accounts})


# View to create a new project
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, user=request.user)  # Pass the current user to the form
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user  # Automatically set the owner of the project
            project.save()
            return redirect('project-list')  # Redirect to the project list view
    else:
        form = ProjectForm(user=request.user)  # Pass the current user to the form on GET request

    return render(request, 'create_project.html', {'form': form})

def search_users(request):
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(full_name__icontains=query)
        user_data = [{"id": user.id, "full_name": user.get_full_name(), "username": user.username} for user in users]
        return JsonResponse({"users": user_data})
    return JsonResponse({"users": []})    


def check_sprint_exists(request, project_id):
    sprint_name = request.GET.get('sprint_name')

    if sprint_name:
        # Check if a sprint with the same name exists in the given project
        exists = Sprint.objects.filter(project_id=project_id, name=sprint_name).exists()
        return JsonResponse({'exists': exists})
    
    return JsonResponse({'exists': False})    

def delete_sprint(request, pk):
    sprint = get_object_or_404(Sprint, pk=pk)
    if request.method == "POST":
        sprint.delete()
        messages.success(request, "Sprint deleted successfully.")
    return redirect('admin:tracker_project_changelist')  # Adjust the redirect as needed



# Function-based view to delete a task
def delete_task(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
        task.delete()
        return JsonResponse({"message": "Task deleted successfully."}, status=200)
    except Task.DoesNotExist:
        return JsonResponse({"error": "Task not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# Function-based view to update a task
def update_task(request, task_id):
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            task = Task.objects.get(pk=task_id)

            # Update task fields
            task.title = data.get("title", task.title)
            task.save()

            return JsonResponse({"message": "Task updated successfully."}, status=200)
        except Task.DoesNotExist:
            return JsonResponse({"error": "Task not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


def add_task(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Validate required data
            sprint_id = data.get("sprint_id")
            title = data.get("title")
            assigned_to_ids = data.get("assigned_to")  # List of user IDs for assignment
            due_date = data.get("due_date")
            status = data.get("status")

            if not sprint_id or not title:
                return JsonResponse({"error": "Sprint ID and title are required."}, status=400)

            # Validate sprint exists
            try:
                sprint = Sprint.objects.get(id=sprint_id)
            except Sprint.DoesNotExist:
                return JsonResponse({"error": "Sprint not found."}, status=404)

            # Validate assigned users exist (optional)
            assigned_to = []
            if assigned_to_ids:
                for user_id in assigned_to_ids:
                    try:
                        user = User.objects.get(id=user_id)
                        assigned_to.append(user)
                    except User.DoesNotExist:
                        return JsonResponse({"error": f"Assigned user with ID {user_id} not found."}, status=404)

            # Validate status is one of the allowed values
            if status not in ['to-do', 'in-progress', 'blocked', 'completed']:
                return JsonResponse({"error": "Invalid status."}, status=400)

            # Create the task
            task = Task.objects.create(
                title=title,
                sprint=sprint,
                due_date=due_date,
                status=status
            )

            # Add the assigned users to the task
            task.assigned_to.set(assigned_to)  # Many-to-many relation
            task.save()

            return JsonResponse({"id": task.id, "message": "Task added successfully."}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


def parse_date(date_str):
    """Helper function to parse date strings."""
    return datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None

@csrf_protect  # Ensure CSRF protection for POST requests
@require_POST  # Ensure only POST requests are accepted
def save_sprint(request, project_id):
    try:
        data = json.loads(request.body)  # This will now work since json is imported
        sprint_name = data.get('sprint_name', '').strip()
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # Check for duplicates before saving
        if Sprint.objects.filter(project_id=project_id, name=sprint_name).exists():
            return JsonResponse({'success': False, 'error': "The sprint with the sprint name already exists for this project. Try editing the same or create the sprint with a different name."}, status=400)

        # Save the sprint
        Sprint.objects.create(
            project_id=project_id,
            name=sprint_name,
            start_date=start_date,
            end_date=end_date,
        )

        return JsonResponse({'success': True}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON format in the request body.'}, status=400)
    
    except KeyError as e:
        return JsonResponse({'success': False, 'error': f'Missing field: {str(e)}'}, status=400)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



def get_user_suggestions(request, project_id):
    query = request.GET.get('query', '').lower()
    try:
        project = Project.objects.get(id=project_id)
        users = project.participants.exclude(id=project.owner.id)
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)

    if query:
        users = users.filter(full_name__icontains=query)
    user_data = users.values('id', 'full_name', 'username')
    return JsonResponse(list(user_data), safe=False)     


@csrf_exempt  # Temporarily disable CSRF check for testing
@require_POST  # Ensure only POST requests are accepted
def save_task(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            title = data.get("title")
            due_date = data.get("due_date")
            status = data.get("status")
            sprint_id = data.get("sprint_id")
            participants = data.get("participants")

            # Validate sprint
            sprint = Sprint.objects.get(id=sprint_id)

            # Validate participants
            users = User.objects.filter(id__in=participants)

            # Create task
            task = Task.objects.create(
                sprint=sprint,
                title=title,
                due_date=due_date,
                status=status
            )
            task.assigned_to.set(users)
            task.save()

            return JsonResponse({"success": True, "message": "Task saved successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)