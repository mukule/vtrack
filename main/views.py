from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
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
from datetime import datetime
from django.template.loader import render_to_string
from django.core.mail import send_mail


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
    time = datetime.now().date()
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
            phone_number = str(visitor.phone)[-9:]

            visitor.save()
            # try:
            #     send_sms(visitor.otp, phone_number)
            # except Exception as e:
               
            #     print(f"Failed to send SMS: {e}")

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
        'time': time,
    }
    return render(request, 'main/index.html', context)


def drivein(request):
    time = datetime.now().date()
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
            phone_number = str(visitor.phone)[-9:]

            visitor.save()
            try:
                send_sms(visitor.otp, phone_number)
            except Exception as e:
               
                print(f"Failed to send SMS: {e}")

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
        'time':time,
    }
    return render(request, 'main/drivein.html', context)

def generate_email_subject(visitor):
    return f"New Visitor Notification: {visitor.full_name}"

def generate_email_body(visitor):
    return render_to_string('main/visitor_notification.html', {'visitor': visitor})

def send_visitor_notification_email(visitor):
    # Use your configured sender email address
    sender_email = settings.EMAIL_FROM

    # Assuming the staff's email is stored in the host's model
    host_email = visitor.host.email

    # Admin email
    admin_email = settings.ADMIN_EMAIL

    # Generate email subject and body
    subject = generate_email_subject(visitor)
    body = generate_email_body(visitor)

    # Send email with plain text content type and CC to admin email
    recipient_list = [host_email, admin_email]
    send_mail(subject, '', sender_email, recipient_list, fail_silently=False, html_message=body)

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
                            try:
                                send_visitor_notification_email(visitor)
                            except Exception as e:
                               
                                print(f"Failed to send email: {e}")

                          
                            return redirect('main:success', visitor_id=visitor.id)

            print('Incorrect OTP!')
            error_messages.append(
                "Incorrect OTP. Ask for the Correct OTP!!.")
        else:
            print('Form errors:', form.errors)
           
            error_messages.extend(form.errors.get('__all__', []))
    else:
        form = VisitorVerificationForm()

    context = {
        'form': form,
        'visitor': visitor,
        'error_messages': error_messages, 
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
    time = datetime.now().date()
    # Get the current date
    current_date = timezone.now().date()

    # Filter visitors for the current day
    visitors = Visitor.objects.filter(created_at__date=current_date).order_by('-created_at')

    context = {'visitors': visitors, 'time': time}

    return render(request, 'main/checkins.html', context)



def v_history(request):
    visitors = Visitor.objects.all().order_by('-created_at').prefetch_related('ratings')
    feedback = Rating.objects.all()
    print(feedback)

    context = {'visitors': visitors}

    return render(request, 'main/v_history.html', context)
    





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

    # Get the feedback URL
    feedback_url = request.build_absolute_uri(reverse('main:rate_visitor', kwargs={'visitor_id': visitor.id}))

    # Print the feedback URL to the terminal
    print(f"Feedback URL for Visitor {visitor.id}: {feedback_url}")

    # Redirect to the check-ins page or any other desired URL
    return redirect('main:checkins')




def create_vp(request):
    if request.method == 'POST':
        form = VisitingPurposeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('main:vp')
    else:
        form = VisitingPurposeForm()

    return render(request, 'main/create_vp.html', {'form': form})


def vp(request):
    purposes = VisitingPurpose.objects.all()
    return render(request, 'main/vp.html', {'vps': purposes})



def rate_visitor(request, visitor_id):
    visitor = get_object_or_404(Visitor, id=visitor_id)

    # Check if a rating already exists for the visitor
    existing_rating = visitor.rating_set.first()

    error_messages = []  # Initialize error_messages

    if existing_rating:
        messages.warning(request, 'You have already submitted a review.You can only submit Once')
        form = RatingForm()
    elif request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.visitor = visitor
            rating.save()
            return redirect('main:r_success') 
        else:
            error_messages = form.errors.values()
            messages.error(request, 'Error submitting rating. Please check the form.')
    else:
        form = RatingForm()

    return render(request, 'main/rate_visitor.html', {'form': form, 'visitor': visitor, 'error_messages': error_messages})


def ro(request):
    ro = RatingOption.objects.all()
    return render(request, 'main/ro.html', {'ros': ro})

def create_ro(request):
    if request.method == 'POST':
        form = RatingOptionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('main:ro')  # Redirect to a success page or another URL
    else:
        form = RatingOptionForm()

    return render(request, 'main/create_ro.html', {'form': form})

def r_success(request):
    return render(request, 'main/r_success.html')