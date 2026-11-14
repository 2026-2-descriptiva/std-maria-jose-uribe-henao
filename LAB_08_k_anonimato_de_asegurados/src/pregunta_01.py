import pandas as pd
import json
from pathlib import Path

def pregunta_01():
    """
    Una aseguradora quiere publicar datos de sus afiliados para que un grupo
    de investigación estudie el costo de los seguros, sin que nadie pueda
    reconocer a una persona. El archivo `data/insurance.csv.gz` tiene una fila
    por afiliado con su edad (`age`), sexo (`sex`), índice de masa corporal
    (`bmi`), número de hijos (`children`), si fuma (`smoker`), región
    (`region`) y el costo de su seguro (`charges`).

    El archivo no tiene nombres ni documentos, pero eso no basta: la edad, el
    sexo, el índice de masa corporal, el número de hijos y la región son
    cuasi-identificadores, porque combinados pueden señalar a una persona.
    `smoker` es el atributo sensible que se quiere proteger.

    En este laboratorio usted va a medir el riesgo de reidentificación y a
    decidir qué publicar. Use estas definiciones:

    - Una clase de equivalencia es un grupo de registros con los mismos
      valores en todos los cuasi-identificadores. Un conjunto de datos cumple
      k-anonimato si toda clase tiene al menos k registros. Use k = 5.
    - `age_group`: `18-29`, `30-39`, `40-49` o `50-64`.
    - `bmi_group`: `bajo peso` (menos de 18.5), `normal` (desde 18.5 y menos
      de 25), `sobrepeso` (desde 25 y menos de 30) u `obesidad` (30 o más).
    - `children_group`: `0`, `1-2` o `3+`.

    Evalúe dos esquemas de generalización:

    - `with_children`: `age_group`, `sex`, `bmi_group`, `children_group` y
      `region`.
    - `without_children`: `age_group`, `sex`, `bmi_group` y `region`; el
      número de hijos no se publica.

    En cada esquema, suprima (no publique) los registros de las clases con
    menos de 5 registros. Luego, entre las clases publicadas, identifique las
    que no tienen diversidad en el atributo sensible, es decir, aquellas en
    las que todos los afiliados fuman o ninguno fuma: en esas clases, saber
    que alguien pertenece a ellas revela si fuma.

    Escriba `submission/privacy_report.json` con estas claves:

    - `original_k`: el menor tamaño de clase usando los cuasi-identificadores
      originales, sin generalizar.
    - `original_unique_records`: cuántos registros son los únicos de su clase
      con los cuasi-identificadores originales.
    - `schemes`: un diccionario con una entrada por esquema (`with_children` y
      `without_children`), cada una con las claves `quasi_identifiers` (la
      lista de columnas del esquema), `equivalence_classes` (clases antes de
      suprimir), `k_before_suppression`, `suppressed_records`,
      `published_records`, `published_classes`,
      `classes_without_smoker_diversity` y
      `records_without_smoker_diversity`.
    - `selected_scheme`: el esquema que suprime menos registros.
    - `mean_charges_original` y `mean_charges_published`: el costo promedio
      de todos los afiliados y el de los registros publicados con el esquema
      seleccionado.
    - `smoker_rate_original` y `smoker_rate_published`: la proporción de
      fumadores en ambos casos.

    Escriba también `submission/insurance_published.csv`, sin el índice de
    Pandas, con los registros publicados del esquema seleccionado, en el
    mismo orden del archivo original, y las columnas del esquema seguidas de
    `smoker` y `charges`.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "original_k": 1,
          "original_unique_records": 1330,
          "schemes": {
            "with_children": {
              "quasi_identifiers": ["age_group", "sex", ...],
              "equivalence_classes": 278,
              ...
            },
            ...
          },
          ...
        }
    """

    ruta = Path(__file__).resolve().parent.parent
    entrada = ruta / "data" / "insurance.csv.gz"
    salida = ruta / "submission"

    df = pd.read_csv(entrada, compression="gzip")

    k = 5

    # Cuasi-identificadores originales
    columnas_originales = ["age", "sex", "bmi", "children", "region"]

    grupos_originales = df.groupby(columnas_originales, dropna=False).size()

    original_k = int(grupos_originales.min())
    original_unique_records = int((grupos_originales == 1).sum())

    # Generalización de variables
    df["age_group"] = pd.cut(
        df["age"],
        bins=[18, 30, 40, 50, 65],
        labels=["18-29", "30-39", "40-49", "50-64"],
        right=False
    )

    df["bmi_group"] = pd.cut(
        df["bmi"],
        bins=[float("-inf"), 18.5, 25, 30, float("inf")],
        labels=["bajo peso", "normal", "sobrepeso", "obesidad"],
        right=False
    )

    df["children_group"] = pd.cut(
        df["children"],
        bins=[-1, 0, 2, float("inf")],
        labels=["0", "1-2", "3+"]
    )

    # Esquemas de generalización
    esquemas = {
        "with_children": [
            "age_group", "sex", "bmi_group",
            "children_group", "region"
        ],
        "without_children": [
            "age_group", "sex", "bmi_group", "region"
        ]
    }

    resultados = {}
    publicados = {}

    for nombre, columnas in esquemas.items():

        grupos = df.groupby(
            columnas, observed=True, dropna=False
        )

        tamaños = grupos["smoker"].transform("size")

        publicado = df.loc[
            tamaños >= k,
            columnas + ["smoker", "charges"]
        ].copy()

        grupos_publicados = publicado.groupby(
            columnas, observed=True, dropna=False
        )

        diversidad = grupos_publicados["smoker"].nunique()

        registros_sin_diversidad = (
            grupos_publicados["smoker"]
            .transform("nunique")
            .eq(1)
            .sum()
        )

        resultados[nombre] = {
            "quasi_identifiers": columnas,
            "equivalence_classes": int(grupos.ngroups),
            "k_before_suppression": int(tamaños.min()),
            "suppressed_records": int((tamaños < k).sum()),
            "published_records": int(len(publicado)),
            "published_classes": int(grupos_publicados.ngroups),
            "classes_without_smoker_diversity": int((diversidad == 1).sum()),
            "records_without_smoker_diversity": int(registros_sin_diversidad)
        }

        publicados[nombre] = publicado

    # Seleccionar el esquema que suprime menos registros
    seleccionado = min(
        resultados,
        key=lambda x: resultados[x]["suppressed_records"]
    )

    df_publicado = publicados[seleccionado]

    # Construir reporte
    reporte = {
        "original_k": original_k,
        "original_unique_records": original_unique_records,
        "schemes": resultados,
        "selected_scheme": seleccionado,
        "mean_charges_original": float(df["charges"].mean()),
        "mean_charges_published": float(df_publicado["charges"].mean()),
        "smoker_rate_original": float(df["smoker"].eq("yes").mean()),
        "smoker_rate_published": float(df_publicado["smoker"].eq("yes").mean())
    }

    # Guardar resultados
    salida.mkdir(parents=True, exist_ok=True)

    df_publicado.to_csv(
        salida / "insurance_published.csv",
        index=False
    )

    with open(salida / "privacy_report.json", "w", encoding="utf-8") as archivo:
        json.dump(reporte, archivo, indent=4, ensure_ascii=False)

    return reporte


pregunta_01()
