import os
import re


def sanitize_filename(filename):
    """
    Remove problematic characters from filename.
    Only allow letters, numbers, underscores, hyphens, and periods.
    """
    # Keep extension separate
    name, ext = os.path.splitext(filename)
    # Remove unwanted characters
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "", name)
    safe_ext = re.sub(r"[^A-Za-z0-9.]", "", ext)
    return safe_name + safe_ext


## Images


def fighter_image_upload_path(instance, filename):
    extension = filename.split(".")[-1]
    new_filename = f"{instance.fname}_{instance.sname}.{extension}"
    safe_filename = sanitize_filename(new_filename)
    return f"fighters/{instance.id}/{safe_filename}"


def promotion_image_upload_path(instance, filename):
    extension = filename.split(".")[-1]
    new_filename = f"{instance.name}.{extension}"
    safe_filename = sanitize_filename(new_filename)
    return f"promotions/{instance.id}/{safe_filename}"


def user_image_upload_path(instance, filename):
    extension = filename.split(".")[-1]
    new_filename = f"{instance.username}.{extension}"
    safe_filename = sanitize_filename(new_filename)
    return f"users/{instance.id}/{safe_filename}"


def event_image_upload_path(instance, filename):
    extension = filename.split(".")[-1]
    new_filename = f"{instance.name}.{extension}"
    safe_filename = sanitize_filename(new_filename)
    return f"events/{instance.id}/{safe_filename}"
