from django.shortcuts import render, redirect
from .models import *
import django
from django.urls import reverse
from django.db.models import Q
import random,string
from urllib import request
from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import bcrypt   
from django.contrib import messages
from .decorators import session_login_required
from django.shortcuts import get_object_or_404

@session_login_required
def dashboard(request):
    user_id = request.session.get("user_id")
    user = CustomUser.objects.get(id=user_id)
    applications = Application.objects.filter(user=user).select_related("job")
    shortlisted_count = applications.filter(status="Shortlisted").count()
    applied_count = applications.filter(status="Applied").count()
    rejected_count = applications.filter(status="Rejected").count()


    profile = Profile.objects.filter(user=user).first()
    jobs = Job.objects.all()

    profile_incomplete = (
        not profile or
        not profile.resume or
        not profile.phone or
        not profile.location
    )

    return render(request, "dashboard.html", {
        "jobs": jobs,
        "user": user,
        "applications": applications,
        "name": user.name,
        "profile": profile,
        "profile_incomplete": profile_incomplete,
        "resume_url": profile.resume.url if profile and profile.resume else "",
         "applications": applications,
    "shortlisted_count": shortlisted_count,
    "applied_count": applied_count,
    "rejected_count": rejected_count,
    })

@session_login_required
def profile(request):
    user_id = request.session.get("user_id")
    user = CustomUser.objects.get(id=user_id)

    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        profile.headline = request.POST.get("headline", "")
        profile.phone = request.POST.get("phone", "")
        profile.location = request.POST.get("location", "")
        profile.skills = request.POST.get("skills", "")

        profile.linkedin = request.POST.get("linkedin", "")
        profile.github = request.POST.get("github", "")
        profile.website = request.POST.get("website", "")

        profile.experience_title = request.POST.get("experience_title", "")
        profile.experience_desc = request.POST.get("experience_desc", "")

        profile.education_title = request.POST.get("education_title", "")
        profile.education_desc = request.POST.get("education_desc", "")

        if "profile_image" in request.FILES:
            profile.profile_image = request.FILES["profile_image"]

        if "resume" in request.FILES:
            profile.resume = request.FILES["resume"]

        profile.save()
        next_dest = request.GET.get('next') or request.POST.get('next')
        job_id = request.GET.get('job_id') or request.POST.get('job_id')
        if next_dest == 'dashboard' and job_id:
            dashboard_url = reverse('dashboard')
            return redirect(f"/dashboard/?open_apply={job_id}")
        return redirect("profile")

    return render(request, "profile.html", {
        "profile": profile,
        "user": user,
        "name": user.name,
    })
@session_login_required
def application_view(request):
    user_id = request.session.get("user_id")
    user = CustomUser.objects.get(id=user_id)
    profile = Profile.objects.filter(user=user).first()
    jobs = Job.objects.all()
    applications = Application.objects.filter(user=user).select_related("job")

    return render(request, "application.html", {
        "applications": applications,
        "user": user,
        "profile": profile,
        "jobs": jobs,
        "name": user.name,
        
    })


@session_login_required
def apply_job(request, job_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    user_id = request.session.get("user_id")
    user = CustomUser.objects.get(id=user_id)
    job = get_object_or_404(Job, id=job_id)
    profile, _ = Profile.objects.get_or_create(user=user)

    # 📄 Resume uploaded from modal
    if request.FILES.get("resume"):
        profile.resume = request.FILES["resume"]
        profile.save()

    # ❌ Profile incomplete
    if not profile.resume or not profile.phone or not profile.location:
        return JsonResponse({
            "status": "incomplete",
            "redirect": f"/profile/?next=dashboard&job_id={job_id}"
        })

    # 🔒 Prevent duplicate apply
    if Application.objects.filter(user=user, job=job).exists():
        return JsonResponse({
            "status": "already_applied",
            "message": "You already applied for this job."
        })

    # ✅ Save application
    Application.objects.create(
        user=user,
        job=job,
        resume=profile.resume
    )

    # 📧 Send confirmation email
    send_mail(
        subject=f"Application Submitted – {job.title}",
        message=f"""
Hello {user.name},

Your application for {job.title} at {job.company} has been submitted successfully.

Regards,
Job House Team
""",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,
    )

    return JsonResponse({
        "status": "success",
        "message": "Application submitted successfully!"
    })

from django.db.models import Q

@session_login_required
def search_jobs(request):
    query = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()

    jobs = Job.objects.all()

    # 🔍 Search priority: title → company → job_description
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company__icontains=query) |
            Q(job_description__icontains=query)
        )

    if location:
        jobs = jobs.filter(location__icontains=location)
      


    # user & profile
    user_id = request.session.get("user_id")
    user = CustomUser.objects.get(id=user_id)
    profile = Profile.objects.filter(user_id=user_id).first()

    profile_incomplete = True
    resume_url = ""

    if profile:
        profile_incomplete = not (
            profile.resume and profile.phone and profile.location
        )
        if profile.resume:
            resume_url = profile.resume.url

    return render(request, "search.html", {
        "jobs": jobs,
        "user": user,
        "query": query,
        "name": user.name,
        "location": location,
        "profile": profile,
        "profile_incomplete": profile_incomplete,
        "resume_url": resume_url,
    })

@session_login_required
def advice_view(request):
    user_id = request.session.get("user_id")
    user = CustomUser.objects.get(id=user_id)
    profile = Profile.objects.filter(user=user).first()
    context={"profile":profile,
                "name": user.name,  
             "user":user}
    return render(request, "career_advice.html", context)




from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

@session_login_required
def contact_send(request):

    profile = Profile.objects.filter(user_id=request.session.get("user_id")).first()
    user_id = request.session.get("user_id")
    user = CustomUser.objects.get(id=user_id)
    context={"profile":profile,
             "name": user.name,
             "user":user}
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        full_message = f"""
        New Contact Message Received

        Name: {name}
        Email: {email}
        Subject: {subject}

        Message:
        {message}
        """

        try:
            send_mail(
                subject=f"Contact Form: {subject}",
                message=full_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],  # author email
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent successfully!")
        except Exception as e:
            messages.error(request, "Failed to send message. Please try again.")

        return redirect("contact")

    return render(request, "contact.html", context)

@session_login_required
def about_view(request):
    user_id = request.session.get("user_id")
    user = CustomUser.objects.get(id=user_id)
    profile = Profile.objects.filter(user_id=request.session.get("user_id")).first()
    context={"profile":profile,
             "name": user.name,
             "user":user}
    return render(request, "about.html", context)

@session_login_required

def logout_view(request):
    request.session.flush()   # 🔥 Clears all session data
    return redirect("login")

# Create your views here.
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = CustomUser.objects.get(email=email)
            hashed_password = user.password.encode('utf-8')
            password_bytes = password.encode('utf-8')

            if bcrypt.checkpw(password_bytes, hashed_password):
                request.session["user_id"] = user.id   # session me store
                return redirect("dashboard")
            else:
                return render(request, "login.html", {"error": "Invalid password"})
        except CustomUser.DoesNotExist:
            return render(request, "login.html", {"error": "Invalid email"})

    return render(request, "login.html")
def home_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    user = CustomUser.objects.get(id=user_id)
    return render(request, "home.html", {"user": user})
# def sign(request):
#     return render(request, "login.htm

def generate_captcha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))




def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        entered_captcha = request.POST.get("captcha")
        session_captcha = request.session.get("captcha_code")

        if entered_captcha != session_captcha:
            messages.error(request, "Captcha does not match!")
            return redirect("forgot_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("forgot_password")

        try:
            user = CustomUser.objects.get(email=email)
            # Generate OTP
            otp = str(random.randint(100000, 999999))
            
            # Store reset data in session
            request.session["reset_data"] = {
                "email": email,
                "new_password": new_password,
                "otp": otp,
            }

            # Send OTP to email
            send_mail(
                subject="Password Reset OTP",
                message=f"Your OTP is {otp}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
            )
            
            return redirect(f"/reset-otp/?email={email}")

        except CustomUser.DoesNotExist:
            messages.error(request, "No account found with this email.")
            return redirect("forgot_password")

    captcha_code = generate_captcha()
    request.session["captcha_code"] = captcha_code
    return render(request, "login.html", {"captcha_code": captcha_code})


def refresh_captcha(request):
    captcha_code = generate_captcha()
    request.session["captcha_code"] = captcha_code
    return JsonResponse({"captcha": captcha_code})
def signup_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # check if email exists
        if CustomUser.objects.filter(email=email).exists():
            return render(request, "login.html", {
                "error": "Email already registered.",
                "show_form": "signup"
            })

        # generate OTP
        otp = str(random.randint(100000, 999999))

        # hash password
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_password = hashed.decode('utf-8')

        # store temp data in session
        request.session["signup_data"] = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "otp": otp,
        }

        # try sending email
        try:
            send_mail(
                subject="Your OTP Verification",
                message=f"Your OTP is {otp}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
            )
        except Exception as e:
            return render(request, "login.html", {
                "error": f"Failed to send email: {e}",
                "show_form": "signup"
            })

        # redirect to OTP page
        return redirect(f"/otp/?email={email}")

    # default get request → open signup/login page
    return render(request, "login.html")

def otp_verify(request):
    email = request.GET.get("email")
    signup_data = request.session.get("signup_data")

    if request.method == "POST":
        entered_otp = request.POST.get("otp")

        if signup_data and entered_otp == signup_data["otp"]:
            user = CustomUser(
                name=signup_data["name"],
                email=signup_data["email"],
                password=signup_data["password"]  # hash password
            )
            user.save()

            request.session["user_id"] = user.id
            del request.session["signup_data"]

            return redirect("dashboard")
        else:
            return render(request, "otp.html", {"email": email, "error": "Invalid OTP"})

    return render(request, "otp.html", {"email": email})


def resend_otp(request):
    signup_data = request.session.get("signup_data")
    reset_data = request.session.get("reset_data")
    
    if signup_data:
        otp = str(random.randint(100000, 999999))
        signup_data["otp"] = otp
        request.session["signup_data"] = signup_data

        send_mail(
            subject="Your New OTP",
            message=f"Your new OTP is {otp}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[signup_data["email"]],
        )
        return redirect(f"/otp/?email={signup_data['email']}")
        
    elif reset_data:
        otp = str(random.randint(100000, 999999))
        reset_data["otp"] = otp
        request.session["reset_data"] = reset_data

        send_mail(
            subject="Your New Password Reset OTP",
            message=f"Your new OTP is {otp}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[reset_data["email"]],
        )
        return redirect(f"/reset-otp/?email={reset_data['email']}")

def reset_otp_verify(request):
    email = request.GET.get("email")
    reset_data = request.session.get("reset_data")

    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        
        if reset_data and entered_otp == reset_data["otp"]:
            try:
                user = CustomUser.objects.get(email=email)
                # Save the new password
                hashed = bcrypt.hashpw(reset_data["new_password"].encode('utf-8'), bcrypt.gensalt())
                user.password = hashed.decode('utf-8')
                user.save()

                # Clear session data
                del request.session["reset_data"]
                
                messages.success(request, "Password reset successful! Please login.")
                return redirect("login")
                
            except CustomUser.DoesNotExist:
                return render(request, "otp.html", {"email": email, "error": "User not found", "is_reset": True})
        else:
            return render(request, "otp.html", {"email": email, "error": "Invalid OTP", "is_reset": True})

    return render(request, "otp.html", {"email": email, "is_reset": True})
