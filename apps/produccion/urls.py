#URLS rutas mediante el frontend podrá acceder a las views.

from rest_framework.routers import DefaultRouter

from apps.produccion.views import (
    OrdenProduccionViewSet,
    OrdenProduccionDetalleViewSet,
    PlanProduccionViewSet,
    PlanDetalleViewSet,
    ColaOperacionViewSet,
    RutaProduccionViewSet,
    PasoRutaViewSet,
    RutaOperacionViewSet,
    OrdenRutaViewSet,
    ProduccionOperacionViewSet,
    DosificacionViewSet,
    ConsumoProduccionViewSet,
    ControlCalidadViewSet,
    TransferenciaProduccionViewSet,
    ResultadoProduccionViewSet,
)

router = DefaultRouter()
router.register(r"ordenes-produccion", OrdenProduccionViewSet,basename="orden-produccion"),
router.register(r"ordenes-produccion-detalles", OrdenProduccionDetalleViewSet,basename="orden-produccion-detalle"),
router.register(r"planes-produccion", PlanProduccionViewSet,basename="plan-produccion"),
router.register(r"planes-detalles", PlanDetalleViewSet,basename="plan-detalle"),
router.register(r"colas-operacion", ColaOperacionViewSet,basename="cola-operacion"),
router.register(r"rutas-produccion", RutaProduccionViewSet,basename="ruta-produccion"),
router.register(r"pasos-ruta", PasoRutaViewSet, basename="paso-ruta"),
router.register(r"rutas-operacion", RutaOperacionViewSet,basename="ruta-operacion"),
router.register(r"ordenes-rutas", OrdenRutaViewSet,basename="orden-ruta"),
router.register(r"producciones-operaciones", ProduccionOperacionViewSet, basename="produccion-operacion")
router.register(r"dosificaciones", DosificacionViewSet, basename="dosificacion"),
router.register(r"consumos-produccion", ConsumoProduccionViewSet, basename="consumo-produccion"),
router.register(r"transferencias", TransferenciaProduccionViewSet, basename="transferencia-produccion"),
router.register(r"controles-calidad", ControlCalidadViewSet,basename="control-calidad"),
router.register(r"resultados-produccion", ResultadoProduccionViewSet,basename="resultado-produccion"),

urlpatterns = router.urls
