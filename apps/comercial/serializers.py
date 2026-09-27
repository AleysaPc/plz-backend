from rest_framework import serializers

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
    PedidoDetalle,
    VarianteColorSolicitada,
)
class CuentaComercialSerializer(serializers.ModelSerializer):
    ejecutivo_nombre = serializers.CharField(
        source="ejecutivo_asignado.get_full_name",
        read_only=True,
    )
    class Meta:
        model = CuentaComercial
        fields = [
             "id",
            "ejecutivo_asignado",
            "ejecutivo_nombre",
            "nombres",
            "apellido_paterno",
            "apellido_materno",
            "tipo_persona",
            "razon_social",
            "identificacion",
            "documento_identidad",
            "numero_documento",
            "telefono",
            "correo",
            "direccion",
            "estado",
            "tipo_relacion",
            "fecha_alta",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "usuario",
            "identificacion",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            'numero_documento': {'required': False, 'allow_blank': True},
        }
class ActividadComercialSerializer(serializers.ModelSerializer):
    estado = serializers.CharField(
        required=False,
        default=ActividadComercial.Estado.PENDIENTE,
    )
    class Meta:
        model = ActividadComercial
        fields = [
            "id",
            "cuenta_comercial",
            "solicitud_comercial",
            "usuario",
            "tipo",
            "descripcion",
            "fecha_programada",
            "fecha_completada",
            "estado",
            "resultado",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "usuario",
            "created_at",
            "updated_at",
        ]

class SolicitudComercialSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudComercial
        fields = [
            "id",
            "cuenta_comercial",
            "fecha",
            "descripcion",
            "prioridad",
            "estado",
            "cantidad_unidades",
            "cantidad_kg",
            "fecha_entrega",
            "observaciones",
            "lugar_entrega",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "usuario",
            "created_at",
            "updated_at",
        ]
class VarianteColorSolicitadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = VarianteColorSolicitada
        fields = [
            "id",
            "especificacion_producto_solicitado",
            "color",
            "cantidad",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

class EspecificacionProductoSolicitadoSerializer(serializers.ModelSerializer):
    variantes_color = VarianteColorSolicitadaSerializer(many=True, required=False,)
    class Meta:
        model = EspecificacionProductoSolicitado
        fields = [
           "id",
            "solicitud_comercial",
            "categoria_producto",
            "material",
            "apto_alimento",
            "micraje",
            "capas",
            "color_bolsa",
            "impresion",
            "color_impresion",
            "tipo_impresion",
            "otras_caracteristicas",
            "opacidad",
            "tratamientos_acabados_especiales",
            "posicion_impresion",
            "variantes_color",
            "cara_impresion",
            "tratamiento_impresion",
            "distancia_impresion_superior",
            "distancia_impresion_inferior",
            "distancia_impresion_izquierda",
            "distancia_impresion_derecha",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ] 

class EspecificacionBolsaSolicitadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EspecificacionBolsaSolicitada
        fields = [
            "id",
            "especificacion_producto_solicitado",
            "ancho_doblado",
            "ancho_desdoblado",
            "largo_doblado",
            "largo_desdoblado",
            "fuelle",
            "fuelle_izquierdo",
            "fuelle_derecho",
            "fuelle_inferior",
            "fuelle_superior",
            "tipo_troquel",
            "tipo_sello",
            "pestana",
            "otras_caracteristicas",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
class EspecificacionBobinaSolicitadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EspecificacionBobinaSolicitada
        fields = [
            "id",
            "especificacion_producto_solicitado",
            "ancho",
            "diametro",
            "diametro_nucleo",
            "longitud",
            "tipo_nucleo",
            "peso",
            "otras_caracteristicas",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

class ComunicacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comunicacion
        fields = [
            "id",
            "solicitud_comercial",
            "usuario",
            "tipo",
            "medio",
            "direccion",
            "asunto",
            "contenido",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "usuario",
            "created_at",
            "updated_at",
        ]

class CotizacionSerializer (serializers.ModelSerializer):
    class Meta:
        model = Cotizacion
        fields = [
            "id",
            "solicitud_comercial",
            "numero",
            "fecha_emision",
            "fecha_vencimiento",
            "estado",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
class CotizacionVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CotizacionVersion
        fields = [
            "id",
            "cotizacion",
            "version",
            "moneda",
            "precio_total",
            "estado",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
class CotizacionDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CotizacionDetalle
        fields = [
            "id",
            "cotizacion_version",
            "producto_version",
            "cantidad",
            "precio_unitario",
            "precio_total",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = [
            "id",
            "cotizacion_version",
            "cuenta_comercial",
            "numero",
            "fecha_pedido",
            "estado",
            "fecha_entrega_comprometida",
            "observaciones",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

class PedidoDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidoDetalle
        fields = [
            "id",
            "pedido",
            "producto_version",
            "cantidad",
            "precio_unitario",
            "precio_total",
            "fecha_entrega_comprometida",
            "observaciones",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]