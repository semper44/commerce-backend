from django.urls import path
from .views import (
    CreatePost,GetProducts,
    DeleteProducts,EditProducts,
    ListAllProductsByCategory,
    ListProductsDetails,
    # EditSingleUserProduct,
    AddToCart,
    RetrieveCart,
    sellers_product,
    ListProductsBSellers,
    PlaceOrder,
    MonthlyOrders,
    ConfirmAndUpdateOrder,
    MostBoughtCategory,
    AllCategories,
    SearchApiview
    )

urlpatterns = [
    path('create/', CreatePost.as_view(), name='product_create'),   
    path('getproduct/', GetProducts.as_view(), name='product_create'),   
    path('admin/deleteproduct/<int:pk>/', DeleteProducts.as_view(), name='product_delete'),   
    path('listproductdetails/<str:pk>/', ListProductsDetails.as_view(), name='listproductdetails'),   
    path('allproducts/<str:pk>/', ListAllProductsByCategory.as_view(), name='allproducts'),   
    path('listproductsbysellers/<str:username>/', ListProductsBSellers.as_view(), name='listproductsbysellers'),   
    path('editproduct/<int:pk>/', EditProducts.as_view(), name='product_edit'),   
    # path('editproduct/user/<int:pk>/', EditSingleUserProduct.as_view(), name='product_edit_details'),   
    path('monthlyorders/', MonthlyOrders.as_view(), name='monthlyorders'),   
    path('addtocart/', AddToCart.as_view(), name='addtocart'),   
    path('retrievecart/', RetrieveCart.as_view(), name='retrievecart'),   
    path('user/allproducts/', sellers_product.as_view(), name='orders'),   
    path('placeorder/', PlaceOrder.as_view(), name='placeorders'),   
    path('search/', SearchApiview.as_view(), name='search'), 
    path('confirmandupdateorder/', ConfirmAndUpdateOrder.as_view(), name='confirmandupdateorder'),   
    path('mostboughtcategory/', MostBoughtCategory.as_view(), name='mostboughtcategory'),   
    path('categories/', AllCategories.as_view(), name='categories'),   
  
    # path('cart/<int:pk>/', CartView.as_view(), name='cart'),   
]