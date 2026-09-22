from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from apps.comercial.models import (
    CuentaComercial,
    ActividadComercial,
    SolicitudComercial,
    EspecificacionProductoSolicitado,
    EspecificacionBobinaSolicitada,
    EspecificacionBolsaSolicitada,
    Comunicacion,
    Cotizacion,
    CotizacionVersion,
    CotizacionDetalle,
    Pedido,
    PedidoDetalle
)
from apps.comercial.serializers import (
    CuentaComercialSerializer,
    ActividadComercialSerializer,
    SolicitudComercialSerializer,
    EspecificacionProductoSolicitadoSerializer,
    EspecificacionBolsaSolicitadaSerializer,
    EspecificacionBobinaSolicitadaSerializer,
    ComunicacionSerializer,
    CotizacionSerializer,
    CotizacionVersionSerializer,
    CotizacionDetalleSerializer,
    PedidoSerializer,
    PedidoDetalleSerializer,
)
from apps.comercial.services.cotizacion_service import (
    crear_cotizacion,
    crear_version_cotizacion,
    agregar_detalle_cotizacion,
    aprobar_cotizacion,
    rechazar_cotizacion,
    cerrar_cotizacion,
)
from apps.comercial.services.pedido_service import (
    crear_pedido_desde_cotizacion,
    crear_detalle_pedido,
    crear_detalles_pedido_desde_cotizacion,
    confirmar_pedido,
    obtener_pedido_con_detalles,
)
from apps.comercial.services.cuenta_comercial_service import (
    crear_cuenta_comercial,
)

User = get_user_model()
class CuentaComercialViewSet(viewsets.ModelViewSet):
    queryset = CuentaComercial.objects.all()
    serializer_class = CuentaComercialSerializer

    def perform_create(self, serializer):
        data = serializer.validated_data.copy()
        data["usuario"] = self.request.user

        crear_cuenta_comercial(data)
    
    @action(detail=True, methods=["patch"])
    def desactivar(self, request, pk=None):
        """
        Desactiva una cuenta comercial sin eliminarla.

        Se conserva todo el historial comercial relacionado
        con la cuenta.
        """

        cuenta = self.get_object()

        cuenta.estado = CuentaComercial.Estado.INACTIVO

        cuenta.save(update_fields=["estado"])

        serializer = self.get_serializer(cuenta)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
        
    @action(detail=True, methods=["patch"])
    def activar(self, request, pk=None):
        cuenta = self.get_object()

        cuenta.estado = CuentaComercial.Estado.CLIENTE
        cuenta.save(update_fields=["estado"])

        serializer = self.get_serializer(cuenta)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ActividadComercialViewSet(viewsets.ModelViewSet):
    queryset = ActividadComercial.objects.all()
    serializer_class = ActividadComercialSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        cuenta_comercial = self.request.query_params.get("cuenta_comercial")

        if cuenta_comercial:
            queryset = queryset.filter(
                cuenta_comercial_id=cuenta_comercial
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(
            usuario=self.request.user,
            estado=ActividadComercial.Estado.PENDIENTE,
        )

class SolicitudComercialViewSet(viewsets.ModelViewSet):
    queryset = SolicitudComercial.objects.all()
    serializer_class = SolicitudComercialSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        cuenta_comercial = self.request.query_params.get("cuenta_comercial")

        if cuenta_comercial:
            queryset = queryset.filter(
                cuenta_comercial_id=cuenta_comercial
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(
            usuario=self.request.user,
            estado=SolicitudComercial.Estado.RECIBIDA,
        )

    @action(detail=True, methods=["get"])
    def detalle(self, request, pk=None):
        solicitud = self.get_object()

        especificacion_producto = (
            EspecificacionProductoSolicitado.objects
            .filter(solicitud_comercial=solicitud)
            .first()
        )

        especificacion_bolsa = None
        especificacion_bobina = None

        if especificacion_producto:
            especificacion_bolsa = (
                EspecificacionBolsaSolicitada.objects
                .filter(
                    especificacion_producto_solicitado=especificacion_producto
                )
                .first()
            )

            especificacion_bobina = (
                EspecificacionBobinaSolicitada.objects
                .filter(
                    especificacion_producto_solicitado=especificacion_producto
                )
                .first()
            )

        return Response({
            "solicitud": SolicitudComercialSerializer(solicitud).data,
            
            "cuentaComercial": CuentaComercialSerializer(
                solicitud.cuenta_comercial
            ).data,

            "especificacionProducto": (
                EspecificacionProductoSolicitadoSerializer(
                    especificacion_producto
                ).data
                if especificacion_producto
                else None
            ),
            "especificacionBolsa": (
                EspecificacionBolsaSolicitadaSerializer(
                    especificacion_bolsa
                ).data
                if especificacion_bolsa
                else None
            ),
            "especificacionBobina": (
                EspecificacionBobinaSolicitadaSerializer(
                    especificacion_bobina
                ).data
                if especificacion_bobina
                else None
            ),
        })
class EspecificacionProductoSolicitadoViewSet(viewsets.ModelViewSet):
    queryset = EspecificacionProductoSolicitado.objects.all()
    serializer_class = EspecificacionProductoSolicitadoSerializer
class EspecificacionBolsaSolicitadaViewSet(viewsets.ModelViewSet):
    queryset = EspecificacionBolsaSolicitada.objects.all()
    serializer_class = EspecificacionBolsaSolicitadaSerializer
class EspecificacionBobinaSolicitadaViewSet(viewsets.ModelViewSet):
    queryset = EspecificacionBobinaSolicitada.objects.all()
    serializer_class = EspecificacionBobinaSolicitadaSerializer

class ComunicacionViewSet(viewsets.ModelViewSet):
    queryset = Comunicacion.objects.all()
    serializer_class = ComunicacionSerializer

    def perform_create(self, serializer):
        serializer.save(
            usuario=self.request.user
        )

class CotizacionViewSet(viewsets.ModelViewSet):
    queryset = Cotizacion.objects.all()
    serializer_class = CotizacionSerializer
    
    @action(detail=False, methods=['post'])
    def crear_desde_solicitud(self, request):
        """Crea una cotización desde una solicitud comercial."""
        solicitud_comercial_id = request.data.get('solicitud_comercial_id')
        fecha_vencimiento = request.data.get('fecha_vencimiento')
        observaciones = request.data.get('observaciones', '')
        
        resultado = crear_cotizacion(
            solicitud_comercial_id=solicitud_comercial_id,
            usuario=request.user,
            fecha_vencimiento=fecha_vencimiento,
            observaciones=observaciones,
        )
        
        if resultado['exito']:
            return Response(resultado, status=status.HTTP_201_CREATED)
        return Response(resultado, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def crear_version(self, request, pk=None):
        """Crea una nueva versión de la cotización."""
        moneda = request.data.get('moneda', 'BOB')
        precio_total = request.data.get('precio_total', 0)
        estado = request.data.get('estado', 'borrador')
        
        resultado = crear_version_cotizacion(
            cotizacion_id=pk,
            usuario=request.user,
            moneda=moneda,
            precio_total=precio_total,
            estado=estado,
        )
        
        if resultado['exito']:
            return Response(resultado, status=status.HTTP_201_CREATED)
        return Response(resultado, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cerrar(self, request, pk=None):
        """Cierra una cotización."""
        observaciones = request.data.get('observaciones', '')
        
        resultado = cerrar_cotizacion(
            cotizacion_id=pk,
            usuario=request.user,
            observaciones=observaciones,
        )
        
        if resultado['exito']:
            return Response(resultado)
        return Response(resultado, status=status.HTTP_400_BAD_REQUEST)
class CotizacionVersionViewSet(viewsets.ModelViewSet):
    queryset = CotizacionVersion.objects.all()
    serializer_class = CotizacionVersionSerializer
    
    @action(detail=True, methods=['post'])
    def agregar_detalle(self, request, pk=None):
        """Agrega un detalle a la versión de cotización."""
        producto_version_id = request.data.get('producto_version_id')
        cantidad = request.data.get('cantidad')
        precio_unitario = request.data.get('precio_unitario')
        
        resultado = agregar_detalle_cotizacion(
            cotizacion_version_id=pk,
            producto_version_id=producto_version_id,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            usuario=request.user,
        )
        
        if resultado['exito']:
            return Response(resultado, status=status.HTTP_201_CREATED)
        return Response(resultado, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        """Aprueba la versión de cotización."""
        observaciones = request.data.get('observaciones', '')
        
        resultado = aprobar_cotizacion(
            cotizacion_version_id=pk,
            usuario=request.user,
            observaciones=observaciones,
        )
        
        if resultado['exito']:
            return Response(resultado)
        return Response(resultado, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        """Rechaza la versión de cotización."""
        motivo = request.data.get('motivo', '')
        
        resultado = rechazar_cotizacion(
            cotizacion_version_id=pk,
            usuario=request.user,
            motivo=motivo,
        )
        
        if resultado['exito']:
            return Response(resultado)
        return Response(resultado, status=status.HTTP_400_BAD_REQUEST)
class CotizacionDetalleViewSet(viewsets.ModelViewSet):
    queryset = CotizacionDetalle.objects.all()
    serializer_class = CotizacionDetalleSerializer

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        cuenta_comercial = self.request.query_params.get("cuenta_comercial")

        if cuenta_comercial:
            queryset = queryset.filter(
                cuenta_comercial_id=cuenta_comercial
            )

        return queryset
    
    @action(detail=False, methods=['post'])
    def crear_desde_cotizacion(self, request):
        """Crea un pedido desde una versión de cotización aprobada."""
        cotizacion_version_id = request.data.get('cotizacion_version_id')
        fecha_entrega_comprometida = request.data.get('fecha_entrega_comprometida')
        observaciones = request.data.get('observaciones', '')
        
        resultado = crear_pedido_desde_cotizacion(
            cotizacion_version_id=cotizacion_version_id,
            usuario=request.user,
            fecha_entrega_comprometida=fecha_entrega_comprometida,
            observaciones=observaciones,
        )
        
        if resultado['exito']:
            return Response(resultado, status=status.HTTP_201_CREATED)
        return Response(resultado, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def crear_detalles_desde_cotizacion(self, request, pk=None):
        """Crea automáticamente los detalles del pedido desde la cotización."""
        resultado = crear_detalles_pedido_desde_cotizacion(
            pedido_id=pk,
            usuario=request.user,
        )
        
        if resultado['exito']:
            return Response(resultado)
        return Response(resultado, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        """Confirma el pedido para iniciar producción."""
        observaciones = request.data.get('observaciones', '')
        
        resultado = confirmar_pedido(
            pedido_id=pk,
            usuario=request.user,
            observaciones=observaciones,
        )
        
        if resultado['exito']:
            return Response(resultado)
        return Response(resultado, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def con_detalles(self, request, pk=None):
        """Obtiene el pedido con todos sus detalles."""
        resultado = obtener_pedido_con_detalles(pedido_id=pk)
        return Response(resultado)
class PedidoDetalleViewSet(viewsets.ModelViewSet):
    queryset = PedidoDetalle.objects.all()
    serializer_class = PedidoDetalleSerializer
