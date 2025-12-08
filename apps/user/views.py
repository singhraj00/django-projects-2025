from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail 
from django.conf import settings
import random
import datetime
from django.utils import timezone
from .form import ProfileForm 
from .utils import send_welcome_email,send_password_reset_confirmation
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


User = get_user_model()

# 🔹 Register View (manual form)
def register_view(request):
    list(messages.get_messages(request))
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('user:register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('user:register')

        user = User.objects.create_user(email=email, first_name=first_name, last_name=last_name,password=password) 
        send_welcome_email(user)
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('user:login')

    return render(request, 'user/register.html')


# 🔹 Login View (manual form)
def login_view(request):
    list(messages.get_messages(request))
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')  # Home page
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('user:login')

    return render(request, 'user/login.html')

@login_required
def change_password_view(request):
    list(messages.get_messages(request))
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        user = request.user

        # 1️⃣ Check old password
        if not user.check_password(old_password):
            messages.error(request, 'Your old password was entered incorrectly.')
            return redirect('user:change_password')

        # 2️⃣ Check if new passwords match
        if new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
            return redirect('user:change_password')

        # 3️⃣ Check password length or strength (optional)
        if len(new_password1) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return redirect('user:change_password')

        # 4️⃣ Update password
        user.set_password(new_password1)
        user.save()
        
        # Send password reset confirmation email
        send_password_reset_confirmation(user)

        # 5️⃣ Keep user logged in after password change
        update_session_auth_hash(request, user)

        messages.success(request, 'Password changed successfully ✅')
        return redirect('/')

    return render(request, 'user/change_password.html')




def forgot_password_view(request):
    list(messages.get_messages(request))
    if request.method == 'POST':
        email = request.POST.get('email')
        User = get_user_model()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'No account found with that email.')
            return redirect('user:forgot_password')

        now = timezone.now()

        # ===== Rate-limit check =====
        attempts = request.session.get('otp_attempts', 0)
        first_attempt_time = request.session.get('first_attempt_time')

        if first_attempt_time:
            first_attempt_time = datetime.datetime.fromisoformat(first_attempt_time)
            diff = (now - first_attempt_time).seconds
            if diff > 600:  # reset every 10 minutes
                attempts = 0
                request.session['first_attempt_time'] = now.isoformat()
        else:
            request.session['first_attempt_time'] = now.isoformat()

        if attempts >= 3:
            messages.error(request, 'Too many OTP requests. Try again after 10 minutes.')
            return redirect('user:forgot_password')

        request.session['otp_attempts'] = attempts + 1

        # ===== OTP re-use window (1 minute) =====
        last_otp_time = request.session.get('otp_generated_time')
        if last_otp_time:
            last_otp_time = datetime.datetime.fromisoformat(last_otp_time)
            if (now - last_otp_time).seconds < 60:
                messages.info(request, 'OTP already sent! Please check your email.')
                return redirect('user:verify_otp')

        # ===== Generate new OTP =====
        otp = random.randint(100000, 999999)
        request.session['reset_email'] = email
        request.session['reset_otp'] = str(otp)
        request.session['otp_generated_time'] = now.isoformat()

        # ===== Render and send professional HTML email =====
        html_content = render_to_string('emails/forgot_password_otp.html', {
            'user': user,
            'otp': otp,
        })
        text_content = strip_tags(html_content)

        email_msg = EmailMultiAlternatives(
            subject='Your Safarnama Password Reset OTP',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send(fail_silently=False)

        messages.success(request, 'OTP sent to your email address.')
        return redirect('user:verify_otp')

    return render(request, 'user/forgot_password.html')



# 2️⃣ Step 2 – Verify OTP
def verify_otp_view(request):
    list(messages.get_messages(request))
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        session_otp = request.session.get('reset_otp')

        if user_otp == session_otp:
            messages.success(request, 'OTP verified successfully!')
            return redirect('user:reset_password')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'user/verify_otp.html')


# 3️⃣ Step 3 – Reset Password
def reset_password_view(request):
    list(messages.get_messages(request))
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('user:reset_password')

        email = request.session.get('reset_email')
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            send_password_reset_confirmation(user)
            # Clear session data
            request.session.pop('reset_email', None)
            request.session.pop('reset_otp', None)

            messages.success(request, 'Password reset successfully! Please login.')
            return redirect('user:login')
        except User.DoesNotExist:
            messages.error(request, 'Something went wrong.')
            return redirect('user:forgot_password')

    return render(request, 'user/reset_password.html')



# 🔹 Logout View
def logout_view(request):
    list(messages.get_messages(request))
    logout(request)
    # Clear all messages
    storage = messages.get_messages(request)
    list(storage)  # marks all as used
    return redirect('/')


@login_required
def profile_view(request):
    return render(request, 'user/profile.html',{'user':request.user})


@login_required
def edit_profile_view(request):
    list(messages.get_messages(request))
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('user:profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'user/edit_profile.html', {'form': form})