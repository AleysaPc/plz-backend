def obtener_ancho_bobina_intermedia(especificacion_bolsa):
    """
    Determina le ancho de la bobina intermedia que será utilizada por 
    los procesos posteriores a la extrusion.
    Regla: 
        - Con fuelle: ancho doblado
        - Sin fuelle: ancho desdoblado
    """
    if especificacion_bolsa is None:
        return None
    
    if especificacion_bolsa.fuelle:
        return especificacion_bolsa.ancho_doblado
    
    return especificacion_bolsa.ancho_desdoblado