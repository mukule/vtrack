from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.models import *
from users.forms import *
import json
from django.core.serializers import serialize
import requests
from django.conf import settings
import requests

rest_api_endpoint = settings.SMS_PROVIDER_API_ENDPOINT
token = settings.SMS_PROVIDER_API_TOKEN
sender_id = settings.SMS_PROVIDER_SENDER_ID


def send_sms(recipient_number, message):
    rest_api_endpoint = settings.SMS_PROVIDER_API_ENDPOINT
    token = settings.SMS_PROVIDER_API_TOKEN
    sender_id = settings.SMS_PROVIDER_SENDER_ID

    # Prepare the request headers
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    # Prepare the request payload
    payload = {
        'sender_id': sender_id,
        'recipient_number': recipient_number,
        'message': message,
    }

    # Make a POST request to the SMS API endpoint
    response = requests.post(rest_api_endpoint, json=payload, headers=headers)

    if response.status_code == 200:
        print("SMS sent successfully.")
    else:
        print(f"Failed to send SMS. Status code: {response.status_code}")


def checkins(request):
    visitors = Visitor.objects.all()
    context = {'visitors': visitors}

    # Send a test SMS when the checkins view is accessed
    test_recipient_number = '@254704122212'
    test_message = 'Test SMS'
    send_sms(test_recipient_number, test_message)

    return render(request, 'main/checkins.html', context)


@login_required
def dashboard(request):
    user = request.user

    # Get all departments
    departments = Department.objects.all()

    # Get staff in each department
    staff_by_department = {str(department.id): list(Staff.objects.filter(department=department).values()) for department in departments}
    staff_by_department_json = json.dumps(staff_by_department)
    
    if request.method == 'POST':
        form = VisitorForm(request.POST)
        print('Form data:', request.POST)
        print('Form is_valid:', form.is_valid())

        if form.is_valid():
            visitor = form.save()
            print('Visitor ID:', visitor.id)
            return redirect('main:success', visitor_id=visitor.id)
        else:
            print('Form errors:', form.errors)
    else:
        form = VisitorForm()
        department_with_staffs = {}

        for department in departments:
            employees_for_department = department.staff_set.all() 
            department_with_staffs[department.id] = serialize(
                'json', employees_for_department)
            
            print(department_with_staffs)

    context = {
        'user': user,
        'form': form,
        'departments': departments,
        'staff_by_department': staff_by_department_json,
        'department_with_staffs': department_with_staffs,
    }
    return render(request, 'main/index.html', context)


def success(request, visitor_id):
    visitor = get_object_or_404(Visitor, id=visitor_id)
    context = {'visitor': visitor}
    return render(request, 'main/success.html', context)
