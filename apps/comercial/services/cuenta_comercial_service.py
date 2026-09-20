from django.db import transaction

from ..models import CuentaComercial, SecuenciaCuentaComercial


@transaction.atomic
def crear_cuenta_comercial(data):
    secuencia = (
        SecuenciaCuentaComercial.objects
        .select_for_update()
        .get(pk=1)
    )

    identificacion = secuencia.siguiente

    cuenta = CuentaComercial.objects.create(
        **data,
        identificacion=identificacion,
    )

    secuencia.siguiente += 1
    secuencia.save(update_fields=["siguiente"])

    return cuenta