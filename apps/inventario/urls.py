#URLS rutas mediante el frontend podrá acceder a las views.
from rest_framework.routers import DefaultRouter
from apps.inventario.views import (
    AlmacenViewSet,
    MateriaPrimaViewSet,
    PinturaViewSet,
    InventarioViewSet,
    MovimientoInventarioViewSet
)

router = DefaultRouter()
router.register(r"almacenes", AlmacenViewSet, basename="almacen")
router.register(r"materias-primas", MateriaPrimaViewSet,basename="materia-prima"),
router.register(r"pinturas", PinturaViewSet,basename="pintura"),
router.register(r"inventarios", InventarioViewSet,basename="inventario"),
router.register(r"movimientos-inventario",MovimientoInventarioViewSet,basename="movimiento-inventario")

urlpatterns = router.urls
