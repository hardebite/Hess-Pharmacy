import json
from .models import *


def cookieCart(request):
        try:
          cart = json.loads(request.COOKIES['cart'])
          # print(cart)
        except:
            cart = {}
        # print("cart:",cart  )
  
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0,'shipping':False}
        cartItems = order['get_cart_items']
        # print(cartItems)
        for i in cart:
          product = Product.objects.get(id=i)
          if product.quantity == 0:
              pass
          else:
              try:
                cartItems += cart[i]['quantity']
                product = Product.objects.get(id=i)
                if product.sales:
                  total = (product.sales_price* cart[i]['quantity'])
                else:
                  total = (product.price* cart[i]['quantity'])
                  pass

                order['get_cart_total'] += total
                order['get_cart_items'] += cart[i]['quantity'] 
                item = {
                  'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageUrl':product.imageUrl,
                    'quantity':product.quantity,
                    'sales':product.sales,
                    'sales_price':product.sales_price
                
                  },
                  'quantity':cart[i]['quantity'],
                  'get_total':total,  
                }
                
                
                items.append(item)
                if product.digital == False:
                  order['shipping']= True
              except:
                pass
        return{"items": items,"order":order,'cartItems':cartItems,}

def cartData(request):
    
    if request.user.is_authenticated:
        try:
          customer = request.user.customer
        except:
          
          customer=  Customer.objects.create(user= request.user,name=request.user,email = request.user.email)
        # print(customer)
        try:
          order, created = Order.objects.get_or_create(customer= customer, complete = False)
        except:
          order.delete()
        items = order.orderitem_set.all()
       
   
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        # print(cookieData)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
        
    return {"items": items,"order":order,'cartItems':cartItems}


def guestOrder(request,data):
      # print("User is not logged in ")
      # print('COOKIES:',request.COOKIES)
      name = data['form']['name']
      email = data['form']['email']
      cookieData= cookieCart(request)
      items = cookieData['items']
      customer, created = Customer.objects.get_or_create(
        email = email,
      )
      customer.name = name
      customer.save()
      order = Order.objects.create(
        customer = customer,
        complete = False
      )
      for item in items :
        product= Product.objects.get(id=item['product']['id'])
        orderItem = OrderItem.objects.create(
            product=product,
            order = order,
            quantity = item['quantity']

        )
        
      return customer , order

