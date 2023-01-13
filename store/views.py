from django.shortcuts import render
from django.views.generic import  View,ListView, DetailView,TemplateView,CreateView,DeleteView
from django.http import JsonResponse , HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required, permission_required
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import json
import datetime
from .models import *
from .utils import *
from .forms import InputForm
from django.contrib import messages
from io import BytesIO
from django.core.files import File
import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders

# Create your views here. 
class MyPaginator(Paginator):
    def validate_number(self, number):
        try:
            return super().validate_number(number)
        except EmptyPage:
            if int(number) > 1:
                # return the last page
                return self.num_pages
            elif int(number) < 1:
                # return the first page
                return 1
            else:
                raise



def store(request):
    paginate_by = 8
    paginator_class = MyPaginator
    page = request.GET.get('page', 1)
    
    if page == None or page == "":
      page = 1
    
    if request.method == 'POST':
        data = cartData(request)
        cartItems = data['cartItems']
        form = InputForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            data= form_data['search']
            list=[]
       
            try:
                products = Product.objects.filter(name__icontains = data)
                paginator = paginator_class(products, paginate_by)
                products = paginator.page(page)
                context = {'products':products,'cartItems':cartItems,}
                context['form']= InputForm()
                
                print(products)
                
                
                return render(request, 'store/store.html', context)
            except Product.DoesNotExist:
                return HttpResponse("no such product")
    else:
      data = cartData(request)
      cartItems = data['cartItems']
      products = Product.objects.order_by('-sales')
      paginator = paginator_class(products, paginate_by)
      products = paginator.page(page)
      context = {'products':products,'cartItems':cartItems,}
      return render(request, 'store/store.html', context)

def cart(request):
    data = cartData(request)
    # print(data)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    # print(data)
    
    for item in items:
      i = 0
      try:
        cart_quantity =  item.product.quantity
      except :
         cart_quantity = item['product']['quantity']
      for item in items:
        try:
          if item.product.quantity<= 0:
            item.delete()
        except:
         if item['product']['quantity']<= 0:
          item.delete() 
    context = {"items": items,"order":order,'cartItems':cartItems,'shipping':False}
    context['form']= InputForm()
    return render(request, 'store/cart.html', context)

def checkout(request):
      # data1 = json.loads(request.body)
      data = cartData(request)
      cartItems = data['cartItems']
      order = data['order']
      items = data['items']
      print(data)
      for item in items:
        try:
          if item.product.quantity<= 0:
            item.delete()
        except:
         if item['product']['quantity']<= 0:
          item.delete() 
      context = {"items": items,"order":order,'cartItems':cartItems,'shipping':False}
      context['form']= InputForm()
      return render(request, 'store/checkout.html', context)



def home(request):
    data = cartData(request)
    cartItems = data['cartItems']
    products= Product.objects.order_by('-id')
    articles= Article.objects.order_by('-id')
    context = {'products':products[0:4],'cartItems':cartItems,'articles':articles[0:2]}
    return render(request, 'store/home.html', context)

def about(request):
    data = cartData(request)
    cartItems = data['cartItems']
    products= Product.objects.all()
    context = {'products':products,'cartItems':cartItems}
    context['form']= InputForm()
    return render(request, 'store/about.html', context)

  
def factory(request):
    data = cartData(request)
    cartItems = data['cartItems']
    products= Product.objects.all()
    context = {'cartItems':cartItems,'products':products}
    context['form']= InputForm()

    return render(request, 'store/factory.html', context)

@permission_required('store.can_view_customer')
def record (request):
    paginate_by = 15
    paginator_class = MyPaginator
    page = request.GET.get('page', 1)
    
    if page == None or page == "":
      page = 1
    data = cartData(request)
    cartItems = data['cartItems']
    # products= Product.objects.all()
    order = OrderItem.objects.all().order_by("-id")
    shipping = ShippingAddress.objects.all()
    
    paginator = paginator_class(order, paginate_by)
    order = paginator.page(page)
    context = {'cartItems':cartItems,'table':order,"info":shipping}
    context['form']= InputForm()

    return render(request, 'store/records.html', context)

def updateItem(request):
  data = json.loads(request.body)
  productId = data['productId']
  action = data['action']
  print("Action:",action)
  print("Product:",productId)
 
  customer = request.user.customer
  product = Product.objects.get(id= productId)
  order, created = Order.objects.get_or_create(customer= customer, complete = False)
  orderItem, created = OrderItem.objects.get_or_create(order= order, product = product)

  if action == 'add':
    orderItem.quantity=(orderItem.quantity+1)
    # print("add")
  elif action == 'remove':
     orderItem.quantity=(orderItem.quantity-1)
  orderItem.save()
  if orderItem.quantity <= 0:
    orderItem.delete()

  return JsonResponse('item was added', safe = False)

def render_pdf_view(request):
  
    template_path = 'store/invoice.html'
    context = {'id':id ,'name':name,'email':email,'order':orders,'total':totals, 'items':items,'address':address,'number':number,'city':city}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    # print(template)
    html = template.render(context)
    # print(html)
    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response,)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response  
     
    
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer= request.user.customer
        order, created = Order.objects.get_or_create(customer= customer, complete = False)  
    else:
      customer,order= guestOrder(request,data)
      total = data['form']['total']
      order.transaction_id = transaction_id
    total = data['form']['total']
    
    order.transaction_id = transaction_id
    if float(total) == float(order.get_cart_total):
      order.complete = True
    final_data = cartData(request)
    # print(final_data)
    global name,email,orders,totals,items,address,city,number, id
    items = final_data['items']
    orders =final_data['order']
    for item in items:
        # print(item['product']['name'])
        try:
          item_id =item.product.id
        except:
          item_id =item['product']['id']
        try:
          new_quantity =item.product.quantity -item.quantity
        except AttributeError:
          new_quantity =item['product']['quantity'] -item['quantity']
        except TypeError:
          new_quantity= 0
        print(new_quantity)
        products = Product.objects.filter(pk=item_id).update(quantity= new_quantity)
 
    order.save()
    
    
    if order.shipping == True:  
          ShippingAddress.objects.create(
            customer=customer,
            order = order,
            address= data['shipping']['address'],
            number = data['shipping']['number'],
            city= data['shipping']['city'],
            state= data['shipping']['state'],
            zipcode= data['shipping']['zipcode'],
          )
    
    
    totals = data['form']['total']
    
    
    
    try:
      name= request.user
      email = request.user.email
      
     
    except:
      name = data['form']['name']
      email= data['form']['email']
    id = transaction_id
    order = orders
    total= totals
    items = items
    address= data['shipping']['address']
    number= data['shipping']['number']
    city= data['shipping']['city']
     
    
    return JsonResponse("payment complete",safe=False)
   
    



def View(request, id):
  product = Product.objects.get(id=id)
  data = cartData(request)
  cartItems = data['cartItems']
  context = {'product':product,'cartItems':cartItems,}
  return render(request, 'store/detail.html', context)



@permission_required('store.can_delete_product')
def delete(request,id):
  product = Product.objects.get(id=id)
  product.delete()
  return HttpResponseRedirect(reverse('store'))


def search(request):
  empty = False
  data = cartData(request)
  cartItems = data['cartItems']
  try:
    search= request.POST['search']
  except:
    search= request.POST.get('search')
  print(search)
  try:
    products = Product.objects.filter(name__icontains = search)
    
    if len(products)== 0:
      empty =True
    context = {'products':products,'cartItems':cartItems,'empty':empty}        
    return render(request, 'store/store.html', context)
  except :
          pass
  return HttpResponseRedirect(reverse('store'))



@permission_required('store.can_add_product')
def add (request):
  data = cartData(request)
  cartItems = data['cartItems']
  context = {'cartItems':cartItems}
  context['form']=InputForm()
  return render(request, 'store/create.html',context ) 

@permission_required('store.can_add_product')
def NewProduct(request):
  if request.method == "POST" :
    name= request.POST.get('name')
    price = float(request.POST.get('price'))
    digital = request.POST.get('digital')
    if digital =="on":
      digital = True
    else:
      digital = False
    quantity = int(request.POST.get('quantity'))
    
    description = request.POST.get('description')
    sales = request.POST.get('sales')
    if sales == "on":
      sales =True
    else :
      sales = False
    try:
      sales_price = float(request.POST.get('sales_price'))
    except:
      sales_price = 0
    image = request.FILES['image']
    print(image)
    fss = FileSystemStorage()
    file = fss.save(image,image)
    file_url = fss.url(file)
    product = Product(name=name,price=price,digital=digital,quantity=quantity,image=image,description=description,sales =sales,sales_price=sales_price)
    product.save()
  
  return HttpResponseRedirect(reverse('store'))

def article(request):
  
  data = cartData(request)
  cartItems = data['cartItems']
  article = Article.objects.all().order_by('-id')
  context = {'cartItems':cartItems,'articles':article}
  return render(request, 'store/article.html', context)

def view_article(request, id):
  article = Article.objects.get(id=id)
  data = cartData(request)
  cartItems = data['cartItems']
  context = {'article':article,'cartItems':cartItems,}
  return render(request, 'store/details2.html', context)

@permission_required('store.can_delete_article')
def delete_article(request,id):
  article = Article.objects.get(id=id)
  article.delete()
  return HttpResponseRedirect(reverse('article'))

@permission_required('store.can_add_article')
def add_article (request):
  data = cartData(request)
  cartItems = data['cartItems']
  context = {'cartItems':cartItems}
  
  return render(request, 'store/create_article.html',context ) 

@permission_required('store.can_add_article')
def NewArticle(request):
  if request.method == "POST" :
    title= request.POST.get('title')
    subtitle = request.POST.get('subtitle')
    body = request.POST.get('body')
    article = Article(title=title,subtitle=subtitle,body=body,)
    article.save()
  
  return HttpResponseRedirect(reverse('article'))


