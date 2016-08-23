from django.db import models
import hashlib
import datetime
import os


def create_hash():
    byte_string = os.urandom(64)
    return hashlib.sha256(byte_string).hexdigest()


class MLModel(models.Model):

    create_date = models.DateTimeField(auto_now_add=True, blank=False)
    description = models.CharField(max_length=256)
    model_hash = models.CharField(max_length=64, default=create_hash, unique=True, blank=False)
    s3_url = models.CharField(max_length=256, unique=True, blank=False)
