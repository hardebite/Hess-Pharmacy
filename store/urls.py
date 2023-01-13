from .import views 
from django.urls import path


# app_name = "store"
urlpatterns = [
    path('',views.home ,name = "home"),
    path('store/',views.store, name = "store"),
    path("cart/",views.cart,name= "cart"),
    path('checkout/',views.checkout, name = 'checkout'),
    path('update_item/',views.updateItem, name = 'update_item'),
    path('process_order/',views.processOrder, name = 'process_order'),
    path("factory/",views.factory,name= "factory"),
     path("render_pdf_view/",views.render_pdf_view,name= "render_pdf_view"),
    path("record/",views.record,name= "record"),
    path("about/",views.about,name= "about"),
    path("detail/<int:id>",views.View,name= "detail"),
    path("delete/<int:id>",views.delete,name= "delete"),
    path("search",views.search,name= "search"),
    path("add/",views.add,name= "add"),
    path("new/",views.NewProduct,name= "new"),
    path("article/",views.article,name= "article"),
    path("add_article/",views.add_article,name= "add_article"),
    path("NewArticle/",views.NewArticle,name= "NewArticle"),
    path("article_detail/<int:id>",views.view_article,name= "article_detail"),
    path("delete_article/<int:id>",views.delete_article,name= "delete_article"),


]