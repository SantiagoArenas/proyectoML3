---
name: employee-retention-analysis-agent
description: Guía para analizar causas de fuga de empleados y proponer acciones de
  retención accionables.
---

# Objetivo
Identificar causas de fuga de empleados y proponer acciones concretas y costo-efectivas para mejorar la retención.

# Datos
- Fuente: `dataSet_RRHH.csv`
- Variables: numéricas y categóricas.
- Requisito: documentar decisiones de limpieza y transformación.

# Metodología
1. Preprocesar variables numéricas y categóricas.
2. Categorizar variables numéricas en niveles (bajo/medio/alto) cuando aporte interpretabilidad.
3. Escalar variables numéricas con `StandardScaler` y `MinMaxScaler` para comparar sensibilidad de algoritmos.
4. Integrar variables transformadas y aplicar one-hot encoding, eliminando redundancias.
5. Evaluar uso de PCA para reducción dimensional e interpretabilidad.
6. Entrenar y comparar clustering con KMeans, K-Prototypes y DBSCAN.

# Evaluación
- Métricas recomendadas: silhouette, inertia (KMeans), y DBCV cuando aplique a clustering por densidad.
- Interpretar cada cluster en lenguaje de negocio: perfil del grupo, posible causa de fuga y riesgo asociado.
- Evitar decisiones basadas únicamente en una métrica; priorizar explicabilidad y accionabilidad.

# Entregables
- Notebook ejecutable (`.ipynb`) con código claro y comentado.
- Visualizaciones consistentes y legibles.
- Resumen para presentación (máximo 10 láminas) con hallazgos y plan de acción.
- Recomendaciones concretas por segmento de empleados.

# Notas
- Se eliminaron 0 párrafos duplicados durante la normalización automática.
- Referencia visual disponible en `mermaidPizarra.mmd`.
