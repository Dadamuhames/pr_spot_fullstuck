from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator, FileExtensionValidator
from datetime import datetime
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils import timezone
from account.models import CustomUser
from admins.models.base_models import BaseSlugFieldModel
# Create your models here.


def is_executor_validate(value):
    user = CustomUser.objects.get(id=int(value))

    if not user.is_executor or not user.business_profile.active:
        raise ValidationError(
            ("This user is not executor"),
            params={'value': value}
        )


def check_order_status(value):
    disalowed_statuses = ['canseled', "completed"]
    # order = Order.objects.get(id=int(value))
    status = value.status

    if status in disalowed_statuses:
        raise ValidationError(
            ("This order is already completed or closed"),
            params={'value': value}
        )


# order categories
class OrderCategories(BaseSlugFieldModel):
    image = models.ImageField(blank=True, null=True)
    title = models.CharField(max_length=255)


# orders
class Order(BaseSlugFieldModel):
    STATUSES = [('acception', "Идет прием заявок"), ("executer_choosen", "Выбран исполнитель"), ('canseled', 'Закза отменен'), ("completed", "Заказ выполнен")]

    costumer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    executor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True,
                                 null=True, related_name='accepted_orders', validators=[is_executor_validate])
    title = models.CharField(max_length=255)
    desc = models.TextField()
    category = models.ForeignKey(OrderCategories, on_delete=models.CASCADE, related_name='orders')
    views = models.IntegerField(validators=[MinValueValidator(0)], default=0, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=255, choices=STATUSES, default="acception")
    active = models.BooleanField(default=True)
    execution_start_date = models.DateTimeField(blank=True, null=True)


    def save(self, *args, **kwargs):
        if not self.id and not self.date:
            self.date = timezone.now()

        return super().save(*args, **kwargs)
    

    def get_executor_offer(self):
        offers = self.offers.filter(executor_offer=True)
        return offers.first()


    def get_ordered_images(self):
        images = self.images.order_by("order")
        return images


# order images
class OrderImages(models.Model):
    parent = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField()
    order = models.IntegerField(validators=[MinValueValidator(1)], blank=True, null=True)



# offers
class Offers(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='offers', validators=[check_order_status])
    executor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='offers', validators=[is_executor_validate])
    days = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.FloatField(validators=[MinValueValidator(1)])
    info = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True,  null=True)
    executor_offer = models.BooleanField(default=False)
    date = models.DateField(blank=True, null=True)
    active = models.BooleanField(default=True)

    
    def save(self, *args, **kwargs):
        if self.executor_offer and self.active:
            # order_offers = self.order.offers.filter(executor_offer=True).exclude(id=self.id)

            # if order_offers.exists():
            #     self.executor_offer = False
            # else:
            self.order.executor = self.executor
            self.order.status = 'executer_choosen'
            self.order.execution_start_date = datetime.now()
            self.order.save()


        if not self.id and not self.date:
            self.date = timezone.now().date()

        return super().save(*args, **kwargs)
    

    class Meta:
        unique_together = [["executor", "order", "active"]]