from django.db import models


def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.csv']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')


class Files(models.Model):
    csv1 = models.FileField(upload_to='data/', validators=[validate_file_extension])
    csv2 = models.FileField(upload_to='data/', validators=[validate_file_extension])
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
