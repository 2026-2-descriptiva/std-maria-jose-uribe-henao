import pandas as pd
from pathlib import Path

def pregunta_11():
    """
    La cuarta columna (`codes`) contiene letras minúsculas separadas por
    comas. Para cada una de esas letras, sume los valores de la segunda
    columna (`value`) de los registros en los que aparece. Retorne un
    diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"a": 122, "b": 49, "c": 91, ...}
    """

    ruta = Path(__file__).resolve().parent.parent / "data" / "data.csv.gz"
    df = pd.read_csv(ruta, sep="\t", compression="gzip", header=None)
    datos = df[[1,3]].copy()
    datos[3] = datos[3].str.split(',')
    datos = datos.explode(3)
    resultado = datos.groupby(3, sort=True)[1].agg('sum')
    respuesta = resultado.to_dict()
    print(respuesta)
    return respuesta


pregunta_11()
