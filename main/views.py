from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.models import *
from users.forms import *
import json
from django.core.serializers import serialize
import requests
from django.conf import settings
import requests
from users.models import *
from datetime import date
from django.db import transaction
from django.core.cache import cache
import random
from django.contrib import messages
from django.http import HttpResponse


def generate_otp():
    """Generate a random 4-digit OTP."""
    return str(random.randint(1000, 9999))


def send_sms(code, phone_number):
    # Obtain Access Token
    token_url = 'https://accounts.jambopay.com/auth/token'
    client_id = settings.CLIENT_ID
    client_secret = settings.SECRET_ID

    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }

    token_response = requests.post(token_url, data=token_data, headers={
                                   'Content-Type': 'application/x-www-form-urlencoded'})

    if token_response.status_code != 200:
        print(f"Token acquisition error: {token_response.text}")
        return f"Token acquisition error: {token_response.text}"

    token = token_response.json().get('access_token')

    # Send SMS
    sms_url = 'https://swift.jambopay.co.ke/api/public/send'
    sender_name = 'PASANDA'
    message = f'Your verification code is {code}'
    callback_url = 'https://pasanda.com/sms/callback'

    sms_data = {
        'sender_name': sender_name,
        'contact': phone_number,
        'message': message,
        'callback': callback_url,
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }

    sms_response = requests.post(
        sms_url, data=json.dumps(sms_data), headers=headers)

    if sms_response.status_code == 200:
        print("SMS sent successfully")
        return "SMS sent successfully"
    else:
        print(f"SMS sending error: {sms_response.text}")
        return f"SMS sending error: {sms_response.text}"


def update_unused_tags():
    # Get all tags marked as used
    used_tags = VisitorTag.objects.filter(used=True)

    # Iterate through the used tags
    for tag in used_tags:
        # Check if the used_at date is not the current date
        if tag.used_at and tag.used_at.date() != date.today():
            with transaction.atomic():
                # If the used_at date is in the past, mark the tag as unused
                if tag.used_at.date() < date.today():
                    tag.used = False
                # If the used_at date is in the future, mark the tag as unused and reset used_at
                else:
                    tag.used = False
                    tag.used_at = None

                # Save the changes to the tag
                tag.save()


@login_required
def dashboard(request):
    update_unused_tags()
    otp = generate_otp()
    print('The otp is: ', otp)
    user = request.user

    # Get all departments
    departments = Department.objects.all()

    # Get staff in each department
    staff_by_department = {str(department.id): list(Staff.objects.filter(
        department=department).values()) for department in departments}
    staff_by_department_json = json.dumps(staff_by_department)

    if request.method == 'POST':
        form = VisitorForm(request.POST)

        if form.is_valid():
            # Don't save the form to the database yet
            visitor = form.save(commit=False)
            visitor.otp = otp  # Assign the generated OTP to the visitor
            print('Assigned otp:', visitor.otp)

            visitor.save()

            return redirect('main:verify', visitor_id=visitor.id)
        else:
            print('Form errors:', form.errors)
    else:
        form = VisitorForm()
        department_with_staffs = {}

        for department in departments:
            employees_for_department = department.staff_set.all()
            department_with_staffs[department.id] = serialize(
                'json', employees_for_department)

    context = {
        'user': user,
        'form': form,
        'departments': departments,
        'staff_by_department': staff_by_department_json,
        'department_with_staffs': department_with_staffs,
    }
    return render(request, 'main/index.html', context)


def drivein(request):
    update_unused_tags()
    otp = generate_otp()
    print('The otp is: ', otp)
    user = request.user

    # Get all departments
    departments = Department.objects.all()

    # Get staff in each department
    staff_by_department = {str(department.id): list(Staff.objects.filter(
        department=department).values()) for department in departments}
    staff_by_department_json = json.dumps(staff_by_department)

    if request.method == 'POST':
        form = DriveInVisitorForm(request.POST)

        if form.is_valid():
            # Don't save the form to the database yet
            visitor = form.save(commit=False)
            visitor.otp = otp  # Assign the generated OTP to the visitor
            print('Assigned otp:', visitor.otp)

            visitor.save()

            return redirect('main:verify', visitor_id=visitor.id)
        else:
            print('Form errors:', form.errors)
    else:
        form = DriveInVisitorForm()
        department_with_staffs = {}

        for department in departments:
            employees_for_department = department.staff_set.all()
            department_with_staffs[department.id] = serialize(
                'json', employees_for_department)

    context = {
        'user': user,
        'form': form,
        'departments': departments,
        'staff_by_department': staff_by_department_json,
        'department_with_staffs': department_with_staffs,
    }
    return render(request, 'main/drivein.html', context)


def verify(request, visitor_id):
    try:
        visitor = Visitor.objects.get(id=visitor_id)
    except Visitor.DoesNotExist:
        messages.error(request, "Visitor not found.")
        return redirect('main:index')

    error_messages = []  # List to store error messages

    if request.method == 'POST':
        form = VisitorVerificationForm(request.POST)

        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            print('Entered OTP:', entered_otp)

            if entered_otp == visitor.otp:
                print('Correct OTP! Visitor ID:', visitor.id)

                # Allocate and activate tag only if OTP is verified
                with transaction.atomic():
                    # Find the first inactive and unused tag
                    last_tag = VisitorTag.objects.filter(
                        is_active=False, used=False).order_by('tag_number').first()

                    if last_tag:
                        # Check if the tag is still inactive and unused (to avoid race conditions)
                        tag_is_active_and_unused = VisitorTag.objects.filter(
                            id=last_tag.id, is_active=False, used=False).exists()

                        if tag_is_active_and_unused:
                            # Update the tag's used status, timestamp, and activation status
                            last_tag.used = True
                            last_tag.used_at = datetime.now()
                            last_tag.is_active = True
                            last_tag.save()

                            # Update the visitor's tag
                            visitor.tag = last_tag

                            # Mark drive_in or walk_in based on the number plate
                            number_plate = visitor.number_plate
                            if number_plate:
                                visitor.drive_in = True
                                visitor.walk_in = False
                            else:
                                visitor.drive_in = False
                                visitor.walk_in = True

                            visitor.verified = True  # Mark the visitor as verified
                            visitor.save()

                            messages.success(
                                request, "OTP verification successful. Visitor verified.")
                            return redirect('main:success', visitor_id=visitor.id)

            print('Incorrect OTP!')
            error_messages.append(
                "Incorrect OTP. Ask for the Correct OTP!!.")
        else:
            print('Form errors:', form.errors)
            # Append form errors to the list of error messages
            error_messages.extend(form.errors.get('__all__', []))
    else:
        form = VisitorVerificationForm()

    context = {
        'form': form,
        'visitor': visitor,
        'error_messages': error_messages,  # Pass error messages to the context
    }
    return render(request, 'main/verify.html', context)


def proceed(request, visitor_id):
    try:
        visitor = Visitor.objects.get(id=visitor_id)
    except Visitor.DoesNotExist:
        messages.error(request, "Visitor not found.")
        return redirect('main:index')

    # Your logic for allocating and activating a tag without OTP verification
    with transaction.atomic():
        # Find the first inactive and unused tag
        last_tag = VisitorTag.objects.filter(
            is_active=False, used=False).order_by('tag_number').first()

        if last_tag:
            # Check if the tag is still inactive and unused (to avoid race conditions)
            tag_is_active_and_unused = VisitorTag.objects.filter(
                id=last_tag.id, is_active=False, used=False).exists()

            if tag_is_active_and_unused:
                # Update the tag's used status, timestamp, and activation status
                last_tag.used = True
                last_tag.used_at = datetime.now()
                last_tag.is_active = True
                last_tag.save()

                # Update the visitor's tag
                visitor.tag = last_tag

                # Mark drive_in or walk_in based on the number plate
                number_plate = visitor.number_plate
                if number_plate:
                    visitor.drive_in = True
                    visitor.walk_in = False
                else:
                    visitor.drive_in = False
                    visitor.walk_in = True
                visitor.save()

                messages.success(
                    request, "Proceeded without OTP verification. Visitor verified.")
                return redirect('main:success', visitor_id=visitor.id)

    # If no tag is allocated, handle the error or redirect as needed
    messages.error(request, "Unable to proceed without allocating a tag.")
    return redirect('main:fail', visitor_id=visitor.id)


def checkins(request):
    visitors = Visitor.objects.all().order_by('-created_at')

    context = {'visitors': visitors}

    # Send a test SMS when the checkins view is accessed
    code = 8080
    phone_number = '704122212'
    # send_sms(code, phone_number)

    return render(request, 'main/checkins.html', context)


def checkin(request):
    return render(request, 'main/checkin.html')


def success(request, visitor_id):
    visitor = get_object_or_404(Visitor, id=visitor_id)
    context = {'visitor': visitor}
    return render(request, 'main/success.html', context)


def fail(request, visitor_id):
    visitor = get_object_or_404(Visitor, id=visitor_id)
    context = {'visitor': visitor}
    return render(request, 'main/fail.html', context)


def tags(request):
    tags = VisitorTag.objects.all()
    context = {
        'tags': tags
    }
    return render(request, 'main/tags.html', context)


def checkouts(request):
    # Retrieve all visitors with inactive tags
    checkouts_list = Visitor.objects.filter(tag__is_active=False)

    context = {
        'checkouts_list': checkouts_list,
    }

    return render(request, 'main/checkouts.html', context)


def checkout_visitor(request, visitor_id):
    # Retrieve the visitor by ID
    visitor = get_object_or_404(Visitor, id=visitor_id)

    # Check if the visitor has an associated tag
    if visitor.tag:
        # Mark the associated tag as inactive
        visitor.tag.is_active = False
        visitor.tag.save()

    # Update the checked_out_at field
    visitor.checked_out_at = timezone.now()
    visitor.save()

    return redirect('main:checkins')
