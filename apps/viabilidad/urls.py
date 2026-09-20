from rest_framework.routers import DefaultRouter
from apps.viabilidad.views import (
    ResultadoViabilidadViewSet,
    EvaluacionViabilidadViewSet,
    EvaluacionComercialViewSet,
    EvaluacionProcesoViewSet,
)
router = DefaultRouter()
router.register(r"resultado-viabilidad", ResultadoViabilidadViewSet,basename="resultado-viabilidad")
router.register(r"evaluacion-viabilidad", EvaluacionViabilidadViewSet,basename="evaluacion-viabilidad")
router.register(r"evaluacion-comercial", EvaluacionComercialViewSet,basename="evaluacion-comercial")
router.register(r"evaluacion-proceso", EvaluacionProcesoViewSet,basename="evaluacion-proceso")

urlpatterns = router.urls