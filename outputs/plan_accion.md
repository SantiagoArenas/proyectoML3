# Plan de accion ejecutado (fuga de empleados)

## Resumen ejecutivo
- Empleados analizados: 4900
- Variables numericas: tenure_years, age, salary_k, performance_score, absenteeism_days, workload_index
- Variables categoricas: Department, Education_Level
- PCA recomendado para 95% varianza: 14 componentes

## Comparacion de modelos
```text
        model             k_or_param  silhouette      inertia  noise_ratio
       dbscan eps=0.5,min_samples=12    0.701702          NaN     0.986939
  kprototypes                      6    0.524018  7211.214041     0.000000
   kmeans_pca                      5    0.379216 14641.051898     0.000000
   kmeans_std                      5    0.354130 16607.014731     0.000000
kmeans_minmax                      5    0.221323 11957.789007     0.000000
```

Modelo seleccionado para accion: **kprototypes**

## Plan de accion por cluster (priorizado por riesgo)
### Cluster 5 | empleados=700 | risk_score=1.155
- Perfil dominante: Department=HR, Education_Level=High School
- Rebalancear carga y definir tope de workload por equipo (4 semanas).
- Programa de bienestar/flexibilidad con seguimiento semanal de ausentismo.
- Revision salarial focalizada para percentil bajo del cluster, no masiva.
- Plan de onboarding extendido y mentoring en primeros 90 dias.

### Cluster 2 | empleados=701 | risk_score=0.114
- Perfil dominante: Department=Sales, Education_Level=PhD
- Revision salarial focalizada para percentil bajo del cluster, no masiva.
- Plan de onboarding extendido y mentoring en primeros 90 dias.

### Cluster 3 | empleados=1348 | risk_score=-0.143
- Perfil dominante: Department=Finance, Education_Level=Master
- Rebalancear carga y definir tope de workload por equipo (4 semanas).

### Cluster 4 | empleados=704 | risk_score=-0.150
- Perfil dominante: Department=Marketing, Education_Level=High School
- Programa de bienestar/flexibilidad con seguimiento semanal de ausentismo.

### Cluster 1 | empleados=700 | risk_score=-0.446
- Perfil dominante: Department=HR, Education_Level=Bachelor
- Revision salarial focalizada para percentil bajo del cluster, no masiva.
- Plan de onboarding extendido y mentoring en primeros 90 dias.
- Retention package para alto desempeno con salario rezagado.

### Cluster 0 | empleados=747 | risk_score=-0.530
- Perfil dominante: Department=Sales, Education_Level=PhD
- Rebalancear carga y definir tope de workload por equipo (4 semanas).

## KPIs de seguimiento (8-12 semanas)
- Reducir ausentismo promedio del cluster de mayor riesgo en >= 10%.
- Reducir workload_index promedio del cluster de mayor riesgo en >= 8%.
- Mejorar performance_score en clusters intervenidos en >= 3 puntos.
- Retencion trimestral del top 20% de riesgo: mejora >= 5 pp.

## Archivos generados
- outputs/model_comparison.csv
- outputs/cluster_profiles.csv
- outputs/plots/cluster_sizes.png
- outputs/plots/cluster_risk.png