import pandas as pd
import numpy as np
from pathlib import Path

def pregunta_01():
    """
    El archivo `data/clusters_report.txt` es un reporte de clústeres de
    palabras clave pensado para ser leído por una persona, no por un programa:
    los encabezados ocupan varias líneas, las columnas están alineadas con
    espacios y la lista de palabras clave de un clúster continúa en las líneas
    siguientes.

    Su tarea es convertir ese reporte en un DataFrame de Pandas con una fila
    por clúster y las columnas:

    - `cluster`: número del clúster, como entero.
    - `cantidad_de_palabras_clave`: como entero.
    - `porcentaje_de_palabras_clave`: como número decimal; por ejemplo, el
      texto `15,9 %` debe quedar como `15.9`.
    - `principales_palabras_clave`: todas las palabras clave del clúster en un
      solo texto, separadas por una coma y un único espacio.

    Retorne el DataFrame.

    Ejemplo del formato de la respuesta (se omite la última columna):

          cluster  cantidad_de_palabras_clave  porcentaje_de_palabras_clave
        0        1                         105                          15.9
        1        2                         102                          15.4
        ...
    """
    ruta = Path(__file__).resolve().parent.parent / "data" / "clusters_report.txt"

    with open(ruta, encoding="utf-8") as archivo:
      lineas = archivo.readlines()

    registros = []

    for linea in lineas:
      partes = linea.split()
      if partes and partes[0].isdigit():
        cluster = int(partes[0])
        cantidad = int(partes[1])
        porcentaje = float(partes[2].replace(",", "."))
        palabras = " ".join(partes[4:])
        registros.append({    "cluster": cluster,
        "cantidad_de_palabras_clave": cantidad,
        "porcentaje_de_palabras_clave": porcentaje,
        "principales_palabras_clave" : palabras})
      elif partes and registros:
        registros[-1]["principales_palabras_clave"] += " " + " ".join(partes)

    df = pd.DataFrame(registros)
    df["principales_palabras_clave"] = df["principales_palabras_clave"].apply(
      lambda texto: ", ".join(p.strip() for p in texto.split(",")).removesuffix(".")
    ) 

    return df


pregunta_01()