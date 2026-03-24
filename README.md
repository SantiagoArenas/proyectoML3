# Proyecto ML3 - Analisis de fuga de empleados

## 1. Objetivo de negocio
Identificar patrones de fuga potencial en empleados para priorizar acciones de retencion costo-efectivas.

En lugar de aplicar medidas generales (por ejemplo, subir salario a toda la empresa), este proyecto segmenta perfiles de empleados y propone acciones focalizadas por cluster.

## 2. Datos
- Fuente: dataSet_RRHH.csv
- Registros: 4900 empleados
- Variables numericas:
  - tenure_years
  - age
  - salary_k
  - performance_score
  - absenteeism_days
  - workload_index
- Variables categoricas:
  - Department
  - Education_Level

## 3. Metodologia
### 3.1 Preprocesamiento
- Categorizacion de variables numericas en bajo/medio/alto con cuantiles (qcut), para mejorar interpretacion.
- Escalado de variables numericas con dos enfoques:
  - StandardScaler
  - MinMaxScaler
- Integracion de variables categoricas + variables categorizadas y One-Hot Encoding (drop_first=True para evitar redundancias).

### 3.2 Reduccion dimensional
- Evaluacion de PCA sobre la matriz estandarizada + OHE.
- Resultado: 14 componentes explican aproximadamente el 95% de la varianza.

### 3.3 Modelos de clustering evaluados
- KMeans con datos estandarizados
- KMeans con datos min-max
- KMeans sobre PCA
- K-Prototypes (mixto numerico + categorico)
- DBSCAN

### 3.4 Criterios de comparacion
- Silhouette
- Inercia (cuando aplica)
- Noise ratio en DBSCAN
- Criterio operativo: se prioriza un modelo accionable (segmentacion usable) frente a un modelo con exceso de ruido.

## 4. Resultados del modelado
Comparacion principal:

- DBSCAN (eps=0.5, min_samples=12): silhouette=0.7017, noise_ratio=0.9869
- K-Prototypes (k=6): silhouette=0.5240, noise_ratio=0.0000
- KMeans PCA (k=5): silhouette=0.3792
- KMeans Std (k=5): silhouette=0.3541
- KMeans MinMax (k=5): silhouette=0.2213

### Decision de modelo
Aunque DBSCAN obtiene la mayor silhouette, clasifica como ruido al 98.69% de los empleados, por lo que no es adecuado para desplegar acciones de retencion a escala.

Se selecciona K-Prototypes por equilibrio entre calidad y accionabilidad.

## 5. Segmentacion y prioridad de riesgo
Se construyo un indice de riesgo relativo por cluster combinando:
- mayor workload_index
- mayor absenteeism_days
- menor performance_score
- menor salary_k
- menor tenure_years

Top de prioridad:

1. Cluster 5 (700 empleados, risk_score=1.155)
- Perfil dominante: HR, High School
- Riesgo mas alto del portafolio

2. Cluster 2 (701 empleados, risk_score=0.114)
- Perfil dominante: Sales, PhD
- Riesgo moderado

Clusters de menor riesgo relativo:
- Cluster 3 (1348 empleados, -0.143)
- Cluster 4 (704 empleados, -0.150)
- Cluster 1 (700 empleados, -0.446)
- Cluster 0 (747 empleados, -0.530)

## 6. Plan de accion ejecutado
### Cluster 5 (prioridad maxima)
- Rebalancear carga y fijar tope de workload por equipo (4 semanas).
- Lanzar programa de bienestar/flexibilidad con seguimiento semanal de ausentismo.
- Revision salarial focalizada al percentil salarial bajo del cluster.
- Plan de onboarding extendido y mentoring en 90 dias.

### Cluster 2
- Revision salarial focalizada.
- Onboarding y mentoring de 90 dias.

### Cluster 3
- Rebalanceo de carga operativa.

### Cluster 4
- Intervencion de bienestar y seguimiento de ausentismo.

### Cluster 1
- Revision salarial focalizada.
- Onboarding y mentoring.
- Retention package para alto desempeno con salario rezagado.

### Cluster 0
- Rebalanceo de carga.

## 7. KPIs de seguimiento (8-12 semanas)
- Reducir ausentismo promedio del cluster de mayor riesgo en al menos 10%.
- Reducir workload_index promedio del cluster de mayor riesgo en al menos 8%.
- Mejorar performance_score en clusters intervenidos en al menos 3 puntos.
- Mejorar retencion trimestral del top 20% de riesgo en al menos 5 puntos porcentuales.

## 8. Artefactos del proyecto
- Reporte de plan de accion: outputs/plan_accion.md
- Comparacion de modelos: outputs/model_comparison.csv
- Perfiles de cluster: outputs/cluster_profiles.csv
- Grafico de tamano de clusters: outputs/plots/cluster_sizes.png
- Grafico de riesgo por cluster: outputs/plots/cluster_risk.png
- Script reproducible: run_plan_accion.py
- Notebook de mejora de agent.md: agent_md_workflow.ipynb

## 9. Como reproducir
### Opcion A: script
1. Activar entorno virtual del proyecto.
2. Ejecutar:

/Users/santi/Desktop/proyectoML3/.venv/bin/python run_plan_accion.py

### Opcion B: notebook
Abrir agent_md_workflow.ipynb y ejecutar celdas para revisar/mejorar agent.md.

## 10. Guion sugerido para PPT (maximo 10 diapositivas)
1. Problema de negocio y objetivo.
2. Datos y variables usadas.
3. Metodologia de preprocesamiento.
4. Modelos de clustering comparados.
5. Resultado de comparacion y seleccion de modelo.
6. Perfil de clusters y riesgo (apoyado en graficos).
7. Plan de accion por clusters prioritarios.
8. KPIs de seguimiento y metas 8-12 semanas.
9. Riesgos, supuestos y siguientes experimentos.
10. Cierre ejecutivo: impacto esperado y roadmap de implementacion.
