"""Primera rebanada: facturación por aseguradora (datos internos no publicados)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def analizar(origen: Path, destino: Path, moneda: str) -> dict:
    datos = pd.read_csv(origen, encoding="utf-8-sig")
    requeridas = {"Estado", "Referencia", "Aseguradora", "Factura", "Emisión", "Total"}
    faltantes = requeridas - set(datos.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {sorted(faltantes)}")

    # La fecha de emisión fija la ventana de seis meses disponibles.
    datos["Emisión"] = pd.to_datetime(datos["Emisión"], format="%Y-%m-%d", errors="coerce")
    datos["Total"] = pd.to_numeric(datos["Total"], errors="coerce")
    datos["Aseguradora"] = datos["Aseguradora"].astype("string").str.strip()
    fecha_fin = datos["Emisión"].max()
    if pd.isna(fecha_fin):
        raise ValueError("No hay fechas de emisión válidas")
    fecha_inicio = fecha_fin - pd.DateOffset(months=6)

    # El estado de pago no cambia el importe facturado: entran Pagada y Pendiente.
    validos = (
        datos["Emisión"].between(fecha_inicio, fecha_fin)
        & datos["Total"].notna()
        & (datos["Total"] > 0)
        & datos["Aseguradora"].notna()
        & (datos["Aseguradora"] != "")
        & datos["Estado"].isin(["Pagada", "Pendiente"])
        & datos["Referencia"].astype(str).str.startswith("3000")
    )
    muestra = datos.loc[validos].copy()
    if muestra.empty:
        raise ValueError("El filtro no dejó facturas para analizar")
    if muestra["Factura"].duplicated().any():
        raise ValueError("Hay identificadores de factura duplicados; revisar antes de sumar")

    resumen = (
        muestra.groupby("Aseguradora", dropna=False)
        .agg(monto=("Total", "sum"), facturas=("Factura", "nunique"),
             referencias=("Referencia", "nunique"))
        .sort_values("monto", ascending=False)
        .reset_index(drop=True)
    )
    total = float(muestra["Total"].sum())
    if abs(float(resumen["monto"].sum()) - total) > 0.01:
        raise AssertionError("La suma por aseguradora no concilia con la fuente filtrada")

    # Las etiquetas por rango ocultan los nombres comerciales en los entregables.
    resumen.insert(0, "aseguradora_anonima", [f"A{i:02d}" for i in range(1, len(resumen) + 1)])
    resumen["participacion_pct"] = 100 * resumen["monto"] / total
    destino.mkdir(parents=True, exist_ok=True)
    resumen.to_csv(destino / "resumen_anonimizado.csv", index=False,
                   columns=["aseguradora_anonima", "monto", "participacion_pct", "facturas", "referencias"])

    resultado = {
        "periodo_desde": fecha_inicio.date().isoformat(),
        "periodo_hasta": fecha_fin.date().isoformat(),
        "moneda": moneda,
        "filas_origen": len(datos),
        "filas_incluidas": len(muestra),
        "filas_excluidas": len(datos) - len(muestra),
        "aseguradoras": len(resumen),
        "facturas": int(muestra["Factura"].nunique()),
        "referencias": int(muestra["Referencia"].nunique()),
        "total": total,
        "top1_pct": float(100 * resumen.head(1)["monto"].sum() / total),
        "top2_pct": float(100 * resumen.head(2)["monto"].sum() / total),
        "top5_pct": float(100 * resumen.head(5)["monto"].sum() / total),
        "top5_facturas_pct": float(100 * resumen.head(5)["facturas"].sum() / len(muestra)),
        "grupos": resumen.to_dict(orient="records"),
    }
    (destino / "resultados.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in resultado.items() if k != "grupos"}, ensure_ascii=False, indent=2))
    return resultado


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, help="Exportación de facturación autorizada o muestra sintética")
    parser.add_argument("--destino", type=Path, default=Path("soporte_preentrega_3"))
    parser.add_argument("--moneda", default="sin especificar", help="Moneda confirmada de los importes")
    args = parser.parse_args()
    analizar(args.csv, args.destino, args.moneda)
