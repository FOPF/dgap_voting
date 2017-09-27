from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
# from social.apps.django_app.default.models import UserSocialAuth
from .models import UserProfile, StudentInfo


@receiver(post_save, sender=User, dispatch_uid='profiles')
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=StudentInfo, dispatch_uid='profiles')
def update_student_info(sender, instance, created, **kwargs):
    try:
        user = User.objects.get(username=instance.vk.split("/")[-1])
        if not user.userprofile.is_aproved:
            user.userprofile.is_approved = True
            user.userprofile.studentinfo = instance
            user.userprofile.group = instance.group
            user.userprofile.save()
            user.first_name = instance.first_name
            user.last_name = instance.last_name
            user.save()
    except Exception:
        pass

    try:
        user = User.objects.get(username=instance.phystech)
        if not user.userprofile.is_aproved:
            user.userprofile.is_approved = True
            user.userprofile.studentinfo = instance
            user.userprofile.group = instance.group
            user.userprofile.save()
            user.first_name = instance.first_name
            user.last_name = instance.last_name
            user.save()
    except Exception:
        pass


# implemented through social_auth_pipeline (view settings.py)
"""@receiver(post_save, sender=UserSocialAuth, dispatch_uid="profiles")
def approve_user(sender, instance, created, **kwargs):
    if created:
        pass"""

