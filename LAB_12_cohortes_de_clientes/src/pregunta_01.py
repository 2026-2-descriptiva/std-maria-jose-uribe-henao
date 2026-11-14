import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def build_cohort_analysis() -> pd.DataFrame:
    """
    Una tienda quiere saber si sus clientes vuelven a comprar después de su
    primera compra. Para responder, agrupe a los clientes en cohortes según
    el mes de su primera compra y mida, mes a mes, qué proporción de cada
    cohorte vuelve a comprar. Use `data/sales.csv.gz`, que tiene una fila por
    orden con su cliente (`CustomerID`) y su fecha (`OrderDate`).

    Use estas definiciones:

    - `cohort_month`: el mes de la primera compra del cliente, escrito como
      `AAAA-MM`.
    - `period_index`: los meses transcurridos desde `cohort_month`; es 0 en el
      mes de la primera compra, 1 en el mes siguiente, y así sucesivamente.
    - `active_customers`: la cantidad de clientes distintos de la cohorte que
      compraron en ese período.
    - `cohort_size`: la cantidad de clientes de la cohorte, es decir, sus
      clientes activos en el período 0.
    - `retention_rate`: `active_customers` sobre `cohort_size`.

    Genere dos archivos en `submission/`:

    1. `cohort_retention.csv`, sin el índice de Pandas, con las columnas
       `cohort_month`, `period_index`, `active_customers`, `cohort_size` y
       `retention_rate`, y una fila por cada combinación cohorte–período
       observada, ordenadas por cohorte y período.

    2. `cohort_retention_heatmap.png`, un mapa de calor de `retention_rate`
       con una fila por cohorte (eje vertical) y una columna por período
       (eje horizontal). Muestre los valores como porcentajes. Los períodos
       que todavía no se pueden observar para una cohorte no significan
       retención cero: déjelos vacíos en el mapa.

    La función también debe retornar la tabla de retención.

    Ejemplo del formato de `cohort_retention.csv`:

        cohort_month,period_index,active_customers,cohort_size,retention_rate
        2022-01,0,100,100,1.0
        2022-01,1,26,100,0.26
        ...
    """

    ruta = Path(__file__).resolve().parent.parent
    entrada = ruta / "data" / "sales.csv.gz"
    salida = ruta / "submission"

    df = pd.read_csv(entrada, compression="gzip")

    df["OrderDate"] = pd.to_datetime(
        df["OrderDate"],
        errors="coerce"
    )

    df = df.dropna(subset=["CustomerID", "OrderDate"]).copy()

    # Identificar el mes de cada compra
    df["order_month"] = df["OrderDate"].dt.to_period("M")

    # Identificar la primera compra de cada cliente
    df["cohort_month"] = (
        df.groupby("CustomerID")["order_month"]
        .transform("min")
    )

    # Calcular los meses transcurridos desde la primera compra
    df["period_index"] = (
        (df["order_month"].dt.year - df["cohort_month"].dt.year) * 12
        + (df["order_month"].dt.month - df["cohort_month"].dt.month)
    )

    # Contar clientes distintos por cohorte y período
    retention = (
        df.groupby(["cohort_month", "period_index"])
        .agg(active_customers=("CustomerID", "nunique"))
        .reset_index()
    )

    # Identificar el tamaño inicial de cada cohorte
    cohort_sizes = (
        retention[retention["period_index"] == 0]
        [["cohort_month", "active_customers"]]
        .rename(columns={"active_customers": "cohort_size"})
    )

    retention = retention.merge(
        cohort_sizes,
        on="cohort_month",
        how="left"
    )

    # Calcular la tasa de retención
    retention["retention_rate"] = (
        retention["active_customers"] / retention["cohort_size"]
    )

    retention["cohort_month"] = retention["cohort_month"].astype(str)

    retention = (
        retention[[
            "cohort_month",
            "period_index",
            "active_customers",
            "cohort_size",
            "retention_rate"
        ]]
        .sort_values(["cohort_month", "period_index"])
        .reset_index(drop=True)
    )

    salida.mkdir(parents=True, exist_ok=True)

    retention.to_csv(
        salida / "cohort_retention.csv",
        index=False
    )

    # Crear matriz de retención
    matriz = retention.pivot(
        index="cohort_month",
        columns="period_index",
        values="retention_rate"
    )

    # Los meses sin compras observadas tienen retención cero
    ultimo_mes = df["order_month"].max()

    for cohorte in matriz.index:
        inicio = pd.Period(cohorte, freq="M")
        meses_observables = (
            (ultimo_mes.year - inicio.year) * 12
            + (ultimo_mes.month - inicio.month)
        )

        columnas_observables = [
            periodo for periodo in matriz.columns
            if periodo <= meses_observables
        ]

        matriz.loc[cohorte, columnas_observables] = (
            matriz.loc[cohorte, columnas_observables].fillna(0)
        )

    # Crear mapa de calor
    fig, ax = plt.subplots(
        figsize=(max(10, len(matriz.columns) * 0.8),
                 max(5, len(matriz.index) * 0.5))
    )

    valores = np.ma.masked_invalid(matriz.to_numpy(dtype=float))

    imagen = ax.imshow(
        valores,
        aspect="auto",
        cmap="YlGnBu",
        vmin=0,
        vmax=1
    )

    ax.set_xticks(range(len(matriz.columns)))
    ax.set_xticklabels(matriz.columns)

    ax.set_yticks(range(len(matriz.index)))
    ax.set_yticklabels(matriz.index)

    ax.set_xlabel("Meses desde la primera compra")
    ax.set_ylabel("Cohorte")
    ax.set_title("Retención mensual de clientes")

    for i in range(len(matriz.index)):
        for j in range(len(matriz.columns)):
            valor = matriz.iloc[i, j]

            if pd.notna(valor):
                ax.text(
                    j, i,
                    f"{valor:.0%}",
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="white" if valor > 0.5 else "black"
                )

    barra = fig.colorbar(imagen, ax=ax)
    barra.set_label("Tasa de retención")
    barra.ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda valor, pos: f"{valor:.0%}")
    )

    fig.tight_layout()

    fig.savefig(
        salida / "cohort_retention_heatmap.png",
        dpi=150,
        bbox_inches="tight"
    )

    plt.close(fig)

    return retention

build_cohort_analysis()
