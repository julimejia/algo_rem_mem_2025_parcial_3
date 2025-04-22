#!/usr/bin/env python

marcos_libres = [0x0,0x1,0x2]
reqs = [ 0x00, 0x12, 0x64, 0x65, 0x8D, 0x8F, 0x19, 0x18, 0xF1, 0x0B, 0xDF, 0x0A ]

segmentos =[ ('.text', 0x00, 0x1A),
             ('.data', 0x40, 0x28), 
              ('.heap', 0x80, 0x1F), 
              ('.stack', 0xC0, 0x22), 
             ]

def procesar(segmentos, reqs, marcos_libres):
    tabla_paginas = {}  
    uso_reciente = []  
    resultados = []

    marco_asignado = {}  # Dirección base de página -> marco físico

    for req in reqs:
        # 1. Verificar si el requerimiento cae en algún segmento válido
        segmento_encontrado = False
        for nombre, base, limite in segmentos:
            if base <= req < base + limite:
                segmento_encontrado = True
                pagina = req // 16  
                offset = req % 16
                break

        if not segmento_encontrado:
            resultados.append((req, 0x1ff, "Segmentation Fault"))
            break

        # 2. Si la página ya está asignada
        if pagina in tabla_paginas:

            if pagina in uso_reciente:
                uso_reciente.remove(pagina)
            uso_reciente.append(pagina)

            direccion_fisica = tabla_paginas[pagina] * 16 + offset
            resultados.append((req, direccion_fisica, "Marco ya estaba asignado"))
            continue

        # 3. Si hay marcos libres
        if marcos_libres:
            marco = marcos_libres.pop(0)
            print
            tabla_paginas[pagina] = marco
            uso_reciente.append(pagina)
            direccion_fisica = marco * 16 + offset
            resultados.append((req, direccion_fisica, "Marco libre asignado"))
            continue

        # 4. No hay marcos libres → aplicar LRU
        pagina_a_reemplazar = uso_reciente.pop(0)  # La menos recientemente usada
        marco = tabla_paginas[pagina_a_reemplazar]
        del tabla_paginas[pagina_a_reemplazar]

        # Asignar nuevo marco a la nueva página
        tabla_paginas[pagina] = marco
        uso_reciente.append(pagina)
        direccion_fisica = marco * 16 + offset
        resultados.append((req, direccion_fisica, "Marco asignado"))

    return resultados
    
def print_results(results):
    for result in results:
        print(f"Req: {result[0]} Direccion Fisica: {result[1]} Acción: {result[2]}")

if __name__ == '__main__':
    results = procesar(segmentos, reqs, marcos_libres)
    print_results(results)

