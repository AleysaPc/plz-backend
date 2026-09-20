#URLS rutas mediante el frontend podrá acceder a las views.

from rest_framework.routers import DefaultRouter

from apps.productos.views import (
    ProductoCategoriaViewSet,
    ProductoViewSet,
    ProductoVersionViewSet,
    EspecificacionBobinaViewSet,
    EspecificacionBolsaViewSet,
)

router = DefaultRouter()
router.register(r"categorias", ProductoCategoriaViewSet,basename="categoria"),
router.register(r"productos",ProductoViewSet,basename="producto"),
router.register(r"versiones",ProductoVersionViewSet,basename="producto-version"),
router.register(r"especificacion-bolsa",EspecificacionBolsaViewSet,basename="especificacion-bolsa"),
router.register(r"especificacion-bobina", EspecificacionBobinaViewSet,basename="especificacion-bobina"),

urlpatterns = router.urls
