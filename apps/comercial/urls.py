from rest_framework.routers import DefaultRouter

from .views import (
    CuentaComercialViewSet,
    ActividadComercialViewSet,
    SolicitudComercialViewSet,
    EspecificacionProductoSolicitadoViewSet,
    EspecificacionBolsaSolicitadaViewSet,
    EspecificacionBobinaSolicitadaViewSet,
    VarianteColorSolicitadaViewSet,
    ComunicacionViewSet,
    CotizacionViewSet,
    CotizacionVersionViewSet,
    CotizacionDetalleViewSet,
    PedidoViewSet,
    PedidoDetalleViewSet,
)

router = DefaultRouter()

router.register(r"cuentas-comerciales", CuentaComercialViewSet, basename="cuenta-comercial")
router.register(r"actividades", ActividadComercialViewSet, basename="actividad-comercial")
router.register(r"solicitudes", SolicitudComercialViewSet, basename="solicitud-comercial")
router.register(r"especificacion-producto-solicitado", EspecificacionProductoSolicitadoViewSet, basename="especificacion-producto")
router.register(r"especificacion-bolsa-solicitada", EspecificacionBolsaSolicitadaViewSet, basename="especificacion-bolsa")
router.register(r"especificacion-bobina-solicitada", EspecificacionBobinaSolicitadaViewSet, basename="especificacion-bobina")
router.register(r"variante-color-solicitada", VarianteColorSolicitadaViewSet, basename="variante-color")
router.register(r"comunicaciones", ComunicacionViewSet, basename="comunicacion")
router.register(r"cotizaciones", CotizacionViewSet, basename="cotizacion")
router.register(r"cotizaciones-versiones", CotizacionVersionViewSet, basename="cotizacion-version")
router.register(r"cotizaciones-detalles", CotizacionDetalleViewSet, basename="cotizacion-detalle")
router.register(r"pedidos", PedidoViewSet, basename="pedido")
router.register(r"pedidos-detalles", PedidoDetalleViewSet, basename="pedido-detalle")

urlpatterns = router.urls