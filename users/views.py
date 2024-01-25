from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import *
from main.decorators import *
from django.contrib.auth.decorators import login_required


def index(request):
    if request.method == "POST":
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                return redirect('main:index')

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = UserLoginForm()

    return render(
        request, "users/index.html",
        context={"form": form}
    )


@access_right
def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"New account created: {user.username}")
            return redirect('login')

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = UserRegisterForm()

    return render(request, "main/index.html",
                  context={"form": form}
                  )


@login_required
def v_reg(request):
    if request.method == 'POST':
        form = VisitorForm(request.POST)
        if form.is_valid():
            visitor = form.save()
            return redirect('users:success', visitor_id=visitor.id)
    else:
        form = VisitorForm()

    return render(request, 'users/v_reg.html', {'form': form})


def success(request, visitor_id):
    visitor = Visitor.objects.get(pk=visitor_id)
    return render(request, 'users/success.html', {'visitor': visitor})


def create_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:departments')
    else:
        form = DepartmentForm()

    return render(request, 'users/create_department.html', {'form': form})


def departments(request):
    departments = Department.objects.all()
    context = {
        'departments': departments
    }
    return render(request, 'users/departments.html', context)


def create_staff(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:staffs')
    else:
        form = StaffForm()

    return render(request, 'users/create_staff.html', {'form': form})


def staffs(request):
    staffs = Staff.objects.all()
    context = {
        'staffs': staffs
    }
    return render(request, 'users/staffs.html', context)


def add_visitor_tag(request):
    if request.method == 'POST':
        form = VisitorTagForm(request.POST)
        if form.is_valid():
            last_number = form.cleaned_data['tag_number']

            # Ensure last_number is at least 1
            last_number = max(1, last_number)

            existing_tags = set(
                VisitorTag.objects.values_list('tag_number', flat=True))
            existing_tags_to_update = existing_tags.intersection(
                range(1, last_number + 1))

            # Update existing tags if necessary
            for tag_number in existing_tags_to_update:
                tag = VisitorTag.objects.get(tag_number=tag_number)
                tag.save()

            # Create missing tags
            missing_tags = set(range(1, last_number + 1)) - existing_tags
            for tag_number in missing_tags:
                VisitorTag.objects.create(tag_number=tag_number)

            # Redirect to a success page after saving
            return redirect('main:tags')
    else:
        form = VisitorTagForm()

    return render(request, 'users/update_tags.html', {'form': form})
