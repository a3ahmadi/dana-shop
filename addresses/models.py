from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="addresses")
    title = models.CharField(max_length=100)
    recipient_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=11)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    complete_address = models.TextField()
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True , null=True)
    updated_at = models.DateTimeField(auto_now=True , null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            if Address.objects.filter(user=self.user).count() >= 3:
                raise ValidationError('حداکثر ۳ آدرس مجاز است')

        if self.is_default:
            Address.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)

        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.title} - {self.state}"
    
    class Meta:
        ordering = ('-created_at',)
