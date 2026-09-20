from rest_framework.routers import DefaultRouter
from apps.recursos.views import (
    EquipoViewSet,
    MaquinariaViewSet,
    VehiculoViewSet,
    AreaProduccionViewSet,
    CapacidadExtrusionViewSet,
    CapacidadFlexografiaViewSet,
    CapacidadConfeccionViewSet,
    CapacidadRefiladoViewSet,
    AnillaViewSet,
    RodilloViewSet,
    ClicheViewSet,
    ClicheParteViewSet,
    DisenoViewSet,
)
router = DefaultRouter()

router.register(r"equipos", EquipoViewSet, basename="equipo")
router.register(r"maquinarias", MaquinariaViewSet, basename="maquinaria")
router.register(r"vehiculos", VehiculoViewSet, basename="vehiculo")
router.register(r"areas-produccion", AreaProduccionViewSet, basename="area-produccion")
router.register(r"capacidades-extrusion", CapacidadExtrusionViewSet, basename="capacidad-extrusion")
router.register(r"capacidades-flexografia", CapacidadFlexografiaViewSet, basename="capacidad-flexografia")
router.register(r"capacidades-confeccion", CapacidadConfeccionViewSet, basename="capacidad-confeccion")
router.register(r"capacidades-refilado", CapacidadRefiladoViewSet, basename="capacidad-refilado")
router.register(r"anillas", AnillaViewSet, basename="anilla")
router.register(r"rodillos", RodilloViewSet, basename="rodillo")
router.register(r"cliches", ClicheViewSet, basename="cliche")
router.register(r"cliches-partes", ClicheParteViewSet, basename="cliche-parte")
router.register(r"disenos", DisenoViewSet, basename="diseno")

urlpatterns = router.urls