import pandas as pd
import numpy as np
from pathlib import Path
import json
import re

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "ventas.csv.gz"
OUTPUT_FILE = BASE_DIR / "submission" / "data_quality_report.json"

REQUIRED_COLUMNS = [
    "supplier_id",
    "supplier",
    "country",
    "city",
    "purchase_date",
    "amount",
    "discount",
    "weight",
    "units",
    "unit_price",
    "contact_email",
]

def normalize_column_names(columns):
    return [
        str(col).replace("\ufeff", "").strip().lower().replace(" ", "_")
        for col in columns
    ]


def get_missing_values(df):
    missing = {}

    for columna in df.columns:
        valores = df[columna].str.strip()
        faltantes = valores.eq("") | valores.eq("N/A")
        missing[columna] = int(faltantes.sum())

    return missing


def get_invalid_emails(series):
    patron = r"[^@\s]+@[^@\s.]+\.[^@\s.]+"

    valores = series.str.strip()
    presentes = ~valores.isin(["", "N/A"])
    validos = valores.str.fullmatch(patron).fillna(False)

    return int((presentes & ~validos).sum())


def get_invalid_units(series):
    valores = series.str.strip()
    presentes = ~valores.isin(["", "N/A"])

    numeros = pd.to_numeric(valores.where(presentes), errors="coerce")

    invalidos = numeros.notna() & (
        (numeros <= 0) | (numeros % 1 != 0)
    )

    return int(invalidos.sum())

def main():
    """
    Antes de limpiar o analizar un conjunto de datos, un analista debe
    documentar qué problemas tiene. En este laboratorio usted no va a limpiar
    `data/ventas.csv.gz`: va a construir un reporte de calidad que deje evidencia
    de sus problemas, tal como están en el archivo.

    Lea `data/ventas.csv.gz` sin modificar sus valores. Para trabajar con los
    encabezados, normalícelos: páselos a minúsculas, elimine los espacios al
    inicio y al final (y cualquier marca BOM) y reemplace los espacios
    internos por `_`. Las columnas requeridas son `supplier_id`, `supplier`,
    `country`, `city`, `purchase_date`, `amount`, `discount`, `weight`,
    `units`, `unit_price` y `contact_email`.

    Escriba el reporte en `submission/data_quality_report.json` con estas
    claves:

    - `row_count`: cantidad de filas de datos.
    - `column_count`: cantidad de columnas.
    - `missing_required_columns`: lista ordenada de columnas requeridas que no
      están en el archivo.
    - `unexpected_columns`: lista ordenada de columnas del archivo que no son
      requeridas.
    - `duplicate_row_count`: cantidad de filas idénticas a una fila anterior.
    - `duplicate_supplier_id_row_count`: cantidad de filas cuyo `supplier_id`
      aparece más de una vez (cuente todas esas filas, no solo las
      repetidas).
    - `missing_value_count_by_column`: diccionario con la cantidad de valores
      faltantes de cada columna. Considere faltantes las celdas vacías y las
      que contienen `N/A`.
    - `invalid_email_count`: cantidad de valores de `contact_email` que no
      tienen la forma `usuario@dominio.extension`.
    - `invalid_unit_count`: cantidad de valores numéricos de `units` que no son
      enteros positivos. Los valores faltantes no se cuentan aquí.
    - `country_values`: lista ordenada de los valores distintos de `country`,
      escritos exactamente como aparecen en el archivo.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "row_count": 103,
          "column_count": 11,
          "missing_required_columns": [],
          ...
          "country_values": [" Colombia ", "CO", ...]
        }
    """

    df = pd.read_csv(
        INPUT_FILE,
        compression="gzip",
        dtype=str,
        keep_default_na=False
    )

    # Normalizar únicamente los nombres de las columnas
    df.columns = normalize_column_names(df.columns)

    # Identificar columnas
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    unexpected_columns = sorted(set(df.columns) - set(REQUIRED_COLUMNS))

    # Contar identificadores repetidos (todas sus apariciones)
    duplicate_ids = (
        int(df["supplier_id"].duplicated(keep=False).sum())
        if "supplier_id" in df.columns else 0
    )

    # Construir reporte
    reporte = {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "missing_required_columns": missing_columns,
        "unexpected_columns": unexpected_columns,
        "duplicate_row_count": int(df.duplicated().sum()),
        "duplicate_supplier_id_row_count": duplicate_ids,
        "missing_value_count_by_column": get_missing_values(df),
        "invalid_email_count": (
            get_invalid_emails(df["contact_email"])
            if "contact_email" in df.columns else 0
        ),
        "invalid_unit_count": (
            get_invalid_units(df["units"])
            if "units" in df.columns else 0
        ),
        "country_values": (
            sorted(df["country"].unique().tolist())
            if "country" in df.columns else []
        ),
    }

    # Crear carpeta y guardar JSON
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as archivo:
        json.dump(reporte, archivo, indent=4, ensure_ascii=False)

    return reporte


if __name__ == "__main__":
    print(main())
