#URLS rutas mediante el frontend podrá acceder a las views.
from rest_framework.routers import DefaultRouter
from apps.despacho.views import (
    DespachoViewSet,
    DespachoDetalleViewSet,
    EntregaViewSet,
)

router = DefaultRouter()
router.register(r"despachos", DespachoViewSet, basename="despacho"),
router.register(r"despachos-detalle", DespachoDetalleViewSet, basename="despacho-detalle"),
router.register(r"entregas", EntregaViewSet, basename="entrega"),


urlpatterns = router.urls
