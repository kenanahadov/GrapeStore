from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name=models.CharField(max_length=120)
    description=models.TextField()
    price=models.DecimalField(max_digits=9,decimal_places=2)
    def __str__(self): return self.name

class ProductImage(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='images')
    url=models.URLField()

class Address(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    full_name=models.CharField(max_length=120)
    line1=models.CharField(max_length=120)
    line2=models.CharField(max_length=120,blank=True)
    city=models.CharField(max_length=60)
    state=models.CharField(max_length=60,blank=True)
    postal_code=models.CharField(max_length=20)
    country=models.CharField(max_length=60,default='USA')
    def __str__(self): return f"{self.full_name}, {self.city}"

class PaymentMethod(models.Model):
    BRANDS=[('VISA','Visa'),('MC','MasterCard'),('AMEX','Amex')]
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    brand=models.CharField(max_length=10,choices=BRANDS)
    last4=models.CharField(max_length=4)
    def __str__(self): return f"{self.get_brand_display()} ••••{self.last4}"

class Wishlist(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    products=models.ManyToManyField(Product,blank=True)

class Order(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    address=models.ForeignKey(Address,on_delete=models.PROTECT)
    payment=models.ForeignKey(PaymentMethod,on_delete=models.PROTECT)
    total=models.DecimalField(max_digits=10,decimal_places=2)
    created=models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
    product=models.ForeignKey(Product,on_delete=models.PROTECT)
    qty=models.PositiveIntegerField()
    price=models.DecimalField(max_digits=9,decimal_places=2)
    def sub_total(self): return self.qty*self.price
