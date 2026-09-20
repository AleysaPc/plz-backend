from rest_framework import viewsets
from apps.notificacion.models import Notificacion
from apps.notificacion.serializers import NotificacionSerializer
class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.select_related(
        "usuario",
    ).all()
    serializer_class = NotificacionSerializer