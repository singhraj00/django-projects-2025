from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from apps.user.models import User

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # GOOGLE is returning email
        email = sociallogin.user.email

        if not email:
            return

        # Check if user already exists
        try:
            existing_user = User.objects.get(email=email)
            # Connect social account to existing user
            sociallogin.connect(request, existing_user)
        except User.DoesNotExist:
            pass
