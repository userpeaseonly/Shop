from django.urls import path
from . import views

app_name = 'shop'
urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<slug:catalog_slug>/', views.product_list, name='product_list_by_catalog'),
    path('<int:product_id>/<slug:product_slug>/', views.product_detail, name='product_detail'),
]