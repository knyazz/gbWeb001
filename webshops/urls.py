from rest_framework.routers import DefaultRouter

from webshops import apis

router = DefaultRouter()

router.register(r'api/category', apis.CategoryViewSet, basename='api_category')
router.register(r'api/order', apis.OrderViewSet, basename='api_order')
router.register(
    r'api/idonly/product', apis.ProductIdOnlyViewSet, basename='api_idonly_product')
router.register(r'api/product', apis.ProductViewSet, basename='api_product')

urlpatterns = router.urls
