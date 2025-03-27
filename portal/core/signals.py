import os
from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from .models import Student, Faculty

@receiver(pre_delete, sender=Student)
def delete_student_profile_picture(sender, instance, **kwargs):
    """
    Signal to delete the profile picture file when a Student instance is deleted
    """
    if instance.profile_picture:
        # Get the file path
        file_path = instance.profile_picture.path
        # Check if file exists and delete it
        if os.path.isfile(file_path):
            os.remove(file_path)

@receiver(pre_delete, sender=Faculty)
def delete_faculty_profile_picture(sender, instance, **kwargs):
    """
    Signal to delete the profile picture file when a Faculty instance is deleted
    """
    if instance.profile_picture:
        # Get the file path
        file_path = instance.profile_picture.path
        # Check if file exists and delete it
        if os.path.isfile(file_path):
            os.remove(file_path)
