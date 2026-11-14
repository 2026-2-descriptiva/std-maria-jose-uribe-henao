import pandas as pd
from pathlib import Path
import unicodedata


def diagnostico(df, etapa="Original"):
    """
    Diagnóstico de calidad de datos.

    Permite comparar los datos originales y los datos limpios.
    """

    print(f"\n{'=' * 60}")
    print(f"DIAGNÓSTICO: {etapa}")
    print(f"{'=' * 60}")

    print("\n1. INFORMACIÓN GENERAL")
    print("Cantidad de filas:", len(df))
    print("Cantidad de columnas:", len(df.columns))
    print("Columnas:", df.columns.tolist())
    print("\nTipos de datos:")
    print(df.dtypes)

    print("\n2. VALORES FALTANTES")
    print(df.isna().sum())

    print("\n3. CAMPOS VACÍOS O CON ESPACIOS")

    for col in df.select_dtypes(include=["object", "string"]).columns:
        vacios = df[col].fillna("").astype(str).str.strip().eq("")
        print(f"{col}: {vacios.sum()}")

    print("\n4. REGISTROS DUPLICADOS")
    print("Duplicados exactos:", df.duplicated().sum())

    if "comuna_ciudadano" in df.columns:
        columnas_sin_comuna = [
            col for col in df.columns
            if col != "comuna_ciudadano"
        ]

        print(
            "Duplicados sin considerar comuna:",
            df.duplicated(subset=columnas_sin_comuna).sum()
        )

    print("\n5. VALORES ÚNICOS EN COLUMNAS DE TEXTO")

    columnas_texto = [
        "sexo",
        "tipo_de_emprendimiento",
        "barrio",
        "línea_credito",
        "comuna_ciudadano"
    ]

    for col in columnas_texto:
        if col in df.columns:
            print(f"\n{col}:")
            print(df[col].value_counts(dropna=False).head(30))

    if "estrato" in df.columns:
        print("\n6. VALORES DE ESTRATO")
        print(df["estrato"].value_counts(dropna=False))

    if "monto_del_credito" in df.columns:
        print("\n7. MONTOS DEL CRÉDITO")

        print("\nMontos más frecuentes:")
        print(df["monto_del_credito"].value_counts().head(30))

        montos = df["monto_del_credito"].astype("string")

        print("\nMontos con símbolos:")
        print(
            montos[
                montos.str.contains(r"[$,.]", regex=True, na=False)
            ].value_counts().head(30)
        )

        numeros = pd.to_numeric(montos, errors="coerce")

        print("\nMontos numéricos menores a 100.000:")
        print(numeros[numeros < 100000].value_counts().head(30))

    if "fecha_de_beneficio" in df.columns:
        print("\n8. ANÁLISIS DE FECHAS")

        fechas = df["fecha_de_beneficio"].astype("string").str.strip()

        print("\nFechas más frecuentes:")
        print(fechas.value_counts().head(15))

        print("\nFechas que comienzan por año:")
        print(
            fechas.str.match(r"^\d{4}[/.-]", na=False).value_counts()
        )

        print("\nFechas potencialmente ambiguas:")

        partes = fechas.str.extract(r"^(\d{1,2})/(\d{1,2})/\d{4}$")

        ambiguas = (
            pd.to_numeric(partes[0], errors="coerce").between(1, 12)
            & pd.to_numeric(partes[1], errors="coerce").between(1, 12)
        )

        print("Cantidad:", ambiguas.sum())
        print(fechas[ambiguas].head(20))

        print("\nFechas con formato AAAA-MM-DD:")
        print(
            fechas.str.match(
                r"^\d{4}-\d{2}-\d{2}$",
                na=False
            ).value_counts()
        )

    columnas_clave = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        "estrato",
        "fecha_de_beneficio",
        "monto_del_credito",
        "línea_credito"
    ]

    if all(col in df.columns for col in columnas_clave):
        print("\n9. POSIBLES DUPLICADOS SIN COMUNA")

        posibles = df[
            df.duplicated(subset=columnas_clave, keep=False)
        ]

        print("Cantidad de filas involucradas:", len(posibles))
        print(posibles.head(10).to_string(index=False))

    print("\n10. POSIBLES DUPLICADOS POR ACENTOS")

    comparacion = df.copy()

    for col in comparacion.select_dtypes(
        include=["object", "string"]
    ).columns:

        if col != "fecha_de_beneficio":
            comparacion[col] = comparacion[col].apply(
                lambda x: (
                    "".join(
                        c for c in unicodedata.normalize("NFKD", x)
                        if not unicodedata.combining(c)
                    )
                    if isinstance(x, str) else x
                )
            )

    print(
        "Duplicados después de normalizar acentos:",
        comparacion.duplicated().sum()
    )

    print("\n11. POSIBLES DUPLICADOS POR FORMATO DE TEXTO")

    comparacion = df.copy()

    columnas_texto = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        "línea_credito"
    ]

    for col in columnas_texto:
        comparacion[col] = (
            comparacion[col]
            .str.lower()
            .str.replace(r"[^\w\s]", " ", regex=True)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

    print("Duplicados con texto normalizado:",
          comparacion.duplicated().sum())

    print("Duplicados originales:",
          df.duplicated().sum())
    
    print("\n12. VARIANTES DE NOMBRES DE BARRIOS")

    barrios = df["barrio"].dropna()

    comparacion = (
        barrios
        .str.replace(r"[^\w\s]", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    variantes = pd.DataFrame({
        "original": barrios,
        "normalizado": comparacion
    })

    variantes = (
        variantes[["original", "normalizado"]]
        .drop_duplicates()
        .sort_values(["normalizado", "original"])
    )

    grupos = variantes.groupby("normalizado")["original"].nunique()
    grupos = grupos[grupos > 1]

    print(
        variantes[
            variantes["normalizado"].isin(grupos.index)
        ].to_string(index=False)
    )

    print(f"\n{'=' * 60}")
    print("FIN DEL DIAGNÓSTICO")
    print(f"{'=' * 60}\n")



def pregunta_01():
    """
    El archivo `data/solicitudes_de_credito.csv.gz` contiene las solicitudes de
    un programa de crédito, pero llegó sucio: tiene una columna de índice que
    no pertenece a los datos, registros duplicados, registros incompletos y
    valores que representan lo mismo escritos de formas distintas en los
    campos de texto, las fechas, el estrato y el monto.

    Su tarea es limpiarlo y guardar el resultado en
    `submission/solicitudes_de_credito.csv`, usando punto y coma (`;`) como
    separador y sin el índice de Pandas.

    El archivo limpio debe cumplir lo siguiente:

    - Contiene solamente las nueve columnas `sexo`, `tipo_de_emprendimiento`,
      `idea_negocio`, `barrio`, `estrato`, `comuna_ciudadano`,
      `fecha_de_beneficio`, `monto_del_credito` y `línea_credito`, en ese
      orden.
    - Los campos de texto están en minúsculas y sus palabras separadas por
      espacios.
    - `estrato` y `monto_del_credito` son números enteros, sin símbolos ni
      separadores de miles.
    - Todas las fechas de `fecha_de_beneficio` usan un mismo formato, por
      ejemplo `AAAA-MM-DD`.
    - No hay registros incompletos. La única excepción es
      `comuna_ciudadano`: sus valores faltantes son parte de los datos
      originales y deben conservarse.
    - No hay registros duplicados.

    Ejemplo del formato del archivo:

        sexo;tipo_de_emprendimiento;idea_negocio;barrio;estrato;...
        femenino;comercio;almacen de ropa en;los cerros el vergel;2;...
        ...
    """

    ruta = Path(__file__).resolve().parent.parent
    entrada = ruta / "data" / "solicitudes_de_credito.csv.gz"
    salida = ruta / "submission" / "solicitudes_de_credito.csv"

    df = pd.read_csv(
        entrada,
        sep=";",
        compression="gzip",
        dtype=str
    )


    # diagnostico(df, "Datos originales")

    # Conservar las columnas necesarias
    columnas = [
        "sexo", "tipo_de_emprendimiento", "idea_negocio",
        "barrio", "estrato", "comuna_ciudadano",
        "fecha_de_beneficio", "monto_del_credito", "línea_credito"
    ]

    df = df[columnas].copy()

    # Normalizar textos
    columnas_texto = [
        "sexo", "tipo_de_emprendimiento", "idea_negocio",
        "barrio", "comuna_ciudadano", "línea_credito"
    ]

    for col in columnas_texto:
        df[col] = (
            df[col]
            .str.lower()
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

    # Limpiar estrato
    df["estrato"] = pd.to_numeric(
        df["estrato"].str.replace(r"[^\d]", "", regex=True),
        errors="coerce"
    )

    # Limpiar monto del crédito
    df["monto_del_credito"] = (
        df["monto_del_credito"]
        .str.strip()
        .str.replace(r"\.00$", "", regex=True)
        .str.replace(r"[^\d]", "", regex=True)
    )

    df["monto_del_credito"] = pd.to_numeric(
        df["monto_del_credito"],
        errors="coerce"
    )

    # Normalizar fechas
    fechas = df["fecha_de_beneficio"].str.strip()

    df["fecha_de_beneficio"] = pd.to_datetime(
        fechas,
        format="mixed",
        dayfirst=True,
        errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    # diagnostico(df, "Después de normalizar")

    # Eliminar registros incompletos
    df = df.dropna(subset=[
        col for col in columnas if col != "comuna_ciudadano"
    ])

    # Convertir números a enteros
    df["estrato"] = df["estrato"].astype(int)
    df["monto_del_credito"] = df["monto_del_credito"].astype(int)

    # Crear una copia para identificar duplicados
    comparacion = df.copy()

    # Normalización general
    for col in columnas_texto:
        df[col] = (
            df[col]
            .str.lower()
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

    # Idea de negocio
    df["idea_negocio"] = (
        df["idea_negocio"]
        .str.replace(r"[^\w\s]", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # Barrio
    df["barrio"] = (
        df["barrio"]
        .str.replace("-", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # Línea de crédito
    df["línea_credito"] = (
        df["línea_credito"]
        .str.replace("-", " ", regex=False)
        .str.strip())


    # Identificar duplicados con la versión normalizada
    duplicados = comparacion.duplicated()

    for col in columnas_texto:
        comparacion[col] = (
            comparacion[col]
            .str.replace(r"[^\w\s]", " ", regex=True)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

    # Eliminar duplicados utilizando la comparación normalizada
    duplicados = comparacion.duplicated()
    df = df.loc[~duplicados].copy()

    # diagnostico(df, "Datos limpios")

    # Guardar archivo
    salida.parent.mkdir(parents=True, exist_ok=True)

    # print("Filas:", len(df))
    # print("Barrios distintos:", df["barrio"].nunique())
    # print("Ideas de negocio distintas:", df["idea_negocio"].nunique())
    # print("\nLíneas de crédito:")
    # print(df["línea_credito"].value_counts())

    df.to_csv(salida, sep=";", index=False)

    return None

pregunta_01()
