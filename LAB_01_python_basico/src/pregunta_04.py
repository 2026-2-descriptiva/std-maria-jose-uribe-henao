import pandas as pd
from pathlib import Path

def pregunta_04():
    """
    Cuente cuántos registros hay en cada mes, usando la fecha de la tercera
    columna (`date`). Represente el mes como un texto de dos dígitos y retorne
    una lista de tuplas `(mes, cantidad)` ordenada por el mes.

    Ejemplo del formato de la respuesta:

        [("01", 3), ("02", 4), ("03", 2), ...]
    """

    ruta = Path(__file__).resolve().parent.parent / "data" / "data.csv.gz"
    df = pd.read_csv(ruta, sep="\t", compression="gzip", header=None)
    df[5] = df.iloc[:,2].str[5:7]
    conteo = df[5].value_counts().sort_index()
    resultado = [(mes, cantidad) for mes, cantidad in conteo.items()]

    return resultado

pregunta_04()
