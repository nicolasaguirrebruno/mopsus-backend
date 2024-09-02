from django.db import models

# Create your models here.


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=120)  # max_length = required
    price = models.DecimalField(decimal_places=2, max_digits=10000)
    reposition_point = models.IntegerField()
    is_active = models.BooleanField(default=True)
    stock = models.IntegerField()
