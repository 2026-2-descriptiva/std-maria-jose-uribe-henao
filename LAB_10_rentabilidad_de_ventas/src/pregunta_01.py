import pandas as pd
import numpy as np
from pathlib import Path

# import gzip
# ruta = Path(__file__).resolve().parent.parent
# entrada = ruta / "data" / "superstore_orders.csv.gz"
# with gzip.open(entrada, "rt", encoding="utf-8-sig") as archivo:
#    for _ in range(5):
#       print(repr(archivo.readline()))

def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
   """
   Una cadena de suministros de oficina vende mucho, pero la gerencia
   sospecha que parte de esas ventas no deja utilidad. El archivo
   `data/superstore_orders.csv.gz` tiene una fila por línea de pedido, con
   el número de pedido (`Order ID`), las ventas (`Sales`), la utilidad
   (`Profit`), el descuento aplicado (`Discount`, como proporción), el
   segmento del cliente (`Customer Segment`) y la categoría del producto
   (`Product Category`). Una utilidad negativa significa que la línea se
   vendió con pérdida.

   Use estas definiciones:

   - Margen (`profit_margin`): utilidad sobre ventas.
   - Línea con pérdida: una línea cuya utilidad es negativa.
   - `loss_line_rate`: la proporción de líneas con pérdida.
   - `lost_profit`: la suma de las pérdidas de las líneas con pérdida,
   escrita como número positivo.
   - Rango de descuento (`discount_band`): `0%` si no hubo descuento,
   `1%-5%` si fue mayor que 0 y hasta 5 %, `6%-10%` si fue mayor que 5 % y
   hasta 10 %, y `más de 10%` en otro caso.

   Genere tres archivos en `submission/`, sin el índice de Pandas y con las
   columnas en el orden indicado:

   1. `profitability_summary.csv`, con una sola fila: `lines` (cantidad de
      líneas), `orders` (pedidos distintos), `sales`, `profit`,
      `profit_margin`, `loss_lines` (cantidad de líneas con pérdida),
      `loss_line_rate` y `lost_profit`.

   2. `discount_summary.csv`, con una fila por rango de descuento, en el
      orden en que se definieron arriba: `discount_band`, `lines`, `sales`,
      `profit`, `profit_margin`, `loss_line_rate` y `lost_profit`.

   3. `priority_segments.csv`, con los cinco segmentos segmento–categoría
      que más utilidad pierden: `Customer Segment`, `Product Category`,
      `lines`, `sales`, `profit`, `profit_margin` y `lost_profit`. Considere
      solamente segmentos con al menos 100 líneas y ordénelos por
      `lost_profit` de mayor a menor.

   La función también debe retornar las tres tablas, en el mismo orden.

   Ejemplo del formato de `discount_summary.csv`:

      discount_band,lines,sales,profit,profit_margin,loss_line_rate,...
      0%,166,170539.05,29472.3789,0.1728,0.488,...
      ...
   """

   ruta = Path(__file__).resolve().parent.parent
   entrada = ruta / "data" / "superstore_orders.csv.gz"
   salida = ruta / "submission"

   df = pd.read_csv(
      entrada,
      compression="gzip",
      sep=";",
      decimal=","
   )
   
   # Identificar las líneas con pérdida
   df["is_loss"] = df["Profit"] < 0

   # Convertir las pérdidas a valores positivos
   df["lost_profit"] = (-df["Profit"].clip(upper=0))

   # Clasificar los descuentos
   df["discount_band"] = pd.cut(
      df["Discount"],
      bins=[-np.inf, 0, 0.05, 0.10, np.inf],
      labels=["0%", "1%-5%", "6%-10%", "más de 10%"],
      include_lowest=True
   )

   # Resumen general
   profitability_summary = pd.DataFrame([{
      "lines": len(df),
      "orders": df["Order ID"].nunique(),
      "sales": df["Sales"].sum(),
      "profit": df["Profit"].sum(),
      "profit_margin": df["Profit"].sum() / df["Sales"].sum(),
      "loss_lines": df["is_loss"].sum(),
      "loss_line_rate": df["is_loss"].mean(),
      "lost_profit": df["lost_profit"].sum()
   }])

   # Resumen por descuento
   discount_summary = (
      df.groupby("discount_band", observed=True)
      .agg(
         lines=("Order ID", "size"),
         sales=("Sales", "sum"),
         profit=("Profit", "sum"),
         loss_line_rate=("is_loss", "mean"),
         lost_profit=("lost_profit", "sum")
      )
      .reset_index()
   )

   discount_summary["profit_margin"] = (
      discount_summary["profit"] / discount_summary["sales"]
   )

   discount_summary = discount_summary[[
      "discount_band", "lines", "sales", "profit",
      "profit_margin", "loss_line_rate", "lost_profit"
   ]]

   # Resumen por segmento y categoría
   priority_segments = (
      df.groupby(["Customer Segment", "Product Category"])
      .agg(
         lines=("Order ID", "size"),
         sales=("Sales", "sum"),
         profit=("Profit", "sum"),
         lost_profit=("lost_profit", "sum")
      )
      .reset_index()
   )

   # Conservar los grupos con al menos 100 líneas
   priority_segments = priority_segments[
      priority_segments["lines"] >= 100
   ].copy()

   priority_segments["profit_margin"] = (
      priority_segments["profit"] / priority_segments["sales"]
   )

   # Seleccionar los cinco grupos con mayores pérdidas
   priority_segments = (
      priority_segments
      .sort_values("lost_profit", ascending=False)
      .head(5)
   )

   priority_segments = priority_segments[[
      "Customer Segment", "Product Category",
      "lines", "sales", "profit",
      "profit_margin", "lost_profit"
   ]]

   # Guardar archivos
   salida.mkdir(parents=True, exist_ok=True)

   profitability_summary.to_csv(
      salida / "profitability_summary.csv",
      index=False
   )

   discount_summary.to_csv(
      salida / "discount_summary.csv",
      index=False
   )

   priority_segments.to_csv(
      salida / "priority_segments.csv",
      index=False
   )

   return profitability_summary, discount_summary, priority_segments


pregunta_01()
