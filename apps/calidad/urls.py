#URLS rutas mediante el frontend podrá acceder a las views.
from rest_framework.routers import DefaultRouter
from apps.calidad.views import (
    ControlCalidadViewSet,
    ControlExtrusionViewSet,
    ControlFlexografiaViewSet,
    ControlConfeccionViewSet,
    ControlRefiladoViewSet,
)

router = DefaultRouter()
router.register(r"controles-calidad", ControlCalidadViewSet, basename="control-calidad"),
router.register(r"controles-extrusion", ControlExtrusionViewSet,basename="control-extrusion"),
router.register(r"controles-flexografia", ControlFlexografiaViewSet, basename="control-flexografia"),
router.register(r"controles-confeccion", ControlConfeccionViewSet,basename="control-confeccion"),
router.register(r"controles-refilado", ControlRefiladoViewSet, basename="control-refilado"),
urlpatterns = router.urls
