# Concentración de facturación por aseguradora

Proyecto de aprendizaje de Augusto Rinaldi Davids, Data Analyst en formación.

## Problema de negocio

El estudio registra facturas en un sistema interno, pero el listado individual no muestra qué aseguradoras concentran los mayores montos. La pregunta de esta rebanada es: **¿qué aseguradoras reúnen la mayor facturación de los últimos seis meses disponibles?** La respuesta ayuda a orientar la revisión comercial.

## Datos y alcance

Se analizó una exportación privada del sistema interno con ocho columnas. El filtro exige referencia del módulo 3000, estado `Pagada` o `Pendiente`, monto positivo, fecha y aseguradora válidos. Los nombres comerciales e identificadores de asegurados no se publican; los códigos A01, A02, etc. se asignan por posición en el ranking.

`Total` es el importe de la factura en pesos argentinos (ARS), según confirmación del responsable de los datos. La exportación no incluye un campo de moneda, costos, horas de trabajo ni tipo de siniestro. Se incluyen facturas pagadas y pendientes; el análisis mide facturación, no cobros.

## Herramientas y método

Python 3 y pandas leen el CSV, validan campos, filtran el período, agrupan por aseguradora y concilian el total con las facturas incluidas. Una presentación muestra el resultado.

Se aplicó CRISP-DM: objetivo de negocio, comprensión y preparación de datos, agrupación, evaluación y comunicación. Este es el Sprint 1 previsto en la Preentrega 2. El cruce con casos y el desglose por tipo quedan para el siguiente sprint.

**Criterios de aceptación:** filtrar las facturas del módulo 3000 emitidas en los seis meses disponibles, con fecha, aseguradora y monto positivo válidos; mostrar el ranking por importe en ARS y el porcentaje del total; comprobar que la suma agrupada coincida con el total filtrado, sin duplicar identificadores de factura.

## Hallazgos

- El análisis permitió ordenar las aseguradoras por importe facturado y calcular su participación en el total.
- Un grupo reducido concentra la mayor parte del importe, lo que orienta una revisión comercial focalizada.
- La aseguradora con mayor importe no fue la de mayor número de facturas. El volumen de facturas por sí solo no explica el monto total.

Son montos facturados, no rentabilidad ni cobros efectivos. Los códigos de aseguradora pueden cambiar al recalcular el ranking. Los importes y las exportaciones reales no se publican en este repositorio.

**Decisión operativa propuesta:** llevar a dirección el ranking y revisar la concentración en las dos primeras aseguradoras. Si en una actualización su peso conjunto baja del 50%, ampliar la revisión comercial al resto de las cinco primeras. El dato de facturación por sí solo no justifica dejar de trabajar con ninguna compañía.

## Cómo ejecutar

1. Instalar Python 3 y pandas: `python -m pip install pandas`.
2. Para probar el código sin datos internos, usar `muestra_sintetica.csv`. Una exportación real solo se usa localmente si está autorizada; no se publica.
3. Ejecutar: `python analisis_preentrega3.py muestra_sintetica.csv --destino resultados --moneda ARS`.
4. Revisar `resultados/resumen_anonimizado.csv` y `resultados/resultados.json`. El script verifica duplicados y conciliación.
