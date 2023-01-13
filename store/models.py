from django.db import models
from django.contrib.auth.models  import User
from sorl.thumbnail import ImageField
from jsonfield import JSONField

# Create your models here.
class Product(models.Model):
    name =  models.CharField(max_length= 200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    digital = models.BooleanField(default=False, null=True, blank=True) 
    quantity = models.IntegerField(null=True, blank=True)
    image  = ImageField(null=True,blank = True)
    description = models.CharField(max_length= 200,null=True,blank = True)
    sales = models.BooleanField(default=False, null=True, blank=True)
    sales_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    def __str__(self):
        return self.name

    @property
    def imageUrl(self):
        try:
            url= self.image.url
        except:
            url = ''
        return url

class Article(models.Model):
    title=models.CharField(max_length=200, null=True)
    subtitle=models.CharField(max_length=200, null=True)
    body = models.CharField(max_length=200, null=True)
    date = models.DateField(auto_now_add= True,blank= True)
    def __str__(self):
        return str(self.title)

class Customer (models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, null=True,blank=True,)
    name= models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=200)
    

    def __str__(self) : 
        return str(self.name)

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL,null=True, blank=True)
    date_ordered = models.DateField(auto_now_add= True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)
    

    def __str__(self):
        return str(self.id)
    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping  

    @property
    def get_cart_total(self):
        orderitems= self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems= self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete= models.SET_NULL,null=True)
    order = models.ForeignKey(Order, on_delete= models.SET_NULL,null=True)
    number = models.CharField( max_length=200)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state= models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateField(auto_now_add=True) 

    def __str__(self) : 
        return self.address

class OrderItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.SET_NULL, null= True)
    order = models.ForeignKey(Order,on_delete=models.SET_NULL, null= True)
    quantity = models.IntegerField(default=0, null=True,blank=True)
    date_added = models.DateField(auto_now_add=True)
    

    @property
    def get_total(self):
        if self.product.sales:
            total = self.product.sales_price * self.quantity
        else:
            total = self.product.price * self.quantity
        return total

# class Order_complete (models.Model):
#     transaction_id = models.CharField(max_length=100, null=True)
#     date_ordered = models.DateField(auto_now_add= True)
#     name = models.CharField(max_length=250, null=True)
#     number = models.CharField( max_length=200)
#     address = models.CharField(max_length=200, null=False)
#     city = models.CharField(max_length=200, null=False)
#     state= models.CharField(max_length=200, null=False)
#     total = models.CharField(max_length=200, null=False)
#     products = JSONField()