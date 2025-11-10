from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

User = get_user_model()

# 🔹 Register View (manual form)
def register_view(request):
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
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('user:login')

    return render(request, 'user/register.html')


# 🔹 Login View (manual form)
def login_view(request):
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

        # 5️⃣ Keep user logged in after password change
        update_session_auth_hash(request, user)

        messages.success(request, 'Password changed successfully ✅')
        return redirect('/')

    return render(request, 'user/change_password.html')


# 🔹 Logout View
def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
def profile_view(request):
    return render(request, 'user/profile.html',{'user':request.user})
