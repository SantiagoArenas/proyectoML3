from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
from kmodes.kprototypes import KPrototypes

np.random.seed(42)

root = Path('.')
out = root / 'outputs'
plots = out / 'plots'
out.mkdir(exist_ok=True)
plots.mkdir(exist_ok=True)

df = pd.read_csv(root / 'dataSet_RRHH.csv')
num_cols = ['tenure_years', 'age', 'salary_k', 'performance_score', 'absenteeism_days', 'workload_index']
cat_cols = ['Department', 'Education_Level']

binned = pd.DataFrame(index=df.index)
for c in num_cols:
    binned[f'{c}_level'] = pd.qcut(df[c], q=3, labels=['bajo', 'medio', 'alto'], duplicates='drop')

cat_all = pd.concat([df[cat_cols].astype(str), binned.astype(str)], axis=1)
X_ohe = pd.get_dummies(cat_all, drop_first=True)

X_num = df[num_cols].copy()
X_std = pd.DataFrame(StandardScaler().fit_transform(X_num), columns=num_cols)
X_mm = pd.DataFrame(MinMaxScaler().fit_transform(X_num), columns=num_cols)

X_std_full = pd.concat([X_std, X_ohe], axis=1)
X_mm_full = pd.concat([X_mm, X_ohe], axis=1)

pca_probe = PCA().fit(X_std_full)
cum_var = np.cumsum(pca_probe.explained_variance_ratio_)
n95 = int(np.argmax(cum_var >= 0.95) + 1)

pca = PCA(n_components=n95, random_state=42)
X_std_pca = pca.fit_transform(X_std_full)

rows = []
cluster_labels = {}

for name, X in [('kmeans_std', X_std_full.values), ('kmeans_minmax', X_mm_full.values), ('kmeans_pca', X_std_pca)]:
    best = None
    for k in range(2, 9):
        km = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels = km.fit_predict(X)
        sil = silhouette_score(X, labels)
        inertia = float(km.inertia_)
        rec = {'model': name, 'k_or_param': k, 'silhouette': float(sil), 'inertia': inertia, 'noise_ratio': 0.0}
        if (best is None) or (sil > best['silhouette']):
            best = rec
            cluster_labels[name] = labels
    rows.append(best)

X_kp_num = X_std[num_cols].to_numpy()
X_kp_cat = df[cat_cols].astype(str).to_numpy()
X_kp = np.concatenate([X_kp_num, X_kp_cat], axis=1)
cat_idx = [len(num_cols), len(num_cols) + 1]
best_kp = None
for k in range(2, 7):
    kp = KPrototypes(n_clusters=k, init='Cao', random_state=42, n_init=5, verbose=0)
    labels = kp.fit_predict(X_kp, categorical=cat_idx)
    sil = silhouette_score(X_kp_num, labels)
    rec = {'model': 'kprototypes', 'k_or_param': k, 'silhouette': float(sil), 'inertia': float(kp.cost_), 'noise_ratio': 0.0}
    if (best_kp is None) or (sil > best_kp['silhouette']):
        best_kp = rec
        cluster_labels['kprototypes'] = labels
rows.append(best_kp)

best_db = None
for eps in [0.4, 0.5, 0.6, 0.8, 1.0, 1.2, 1.5]:
    for ms in [8, 12, 16, 24]:
        db = DBSCAN(eps=eps, min_samples=ms)
        labels = db.fit_predict(X_std_full.values)
        mask = labels != -1
        n_clusters = len(set(labels[mask]))
        noise_ratio = float((labels == -1).mean())
        if n_clusters >= 2 and mask.sum() > 30:
            sil = silhouette_score(X_std_full.values[mask], labels[mask])
            rec = {
                'model': 'dbscan',
                'k_or_param': f'eps={eps},min_samples={ms}',
                'silhouette': float(sil),
                'inertia': np.nan,
                'noise_ratio': noise_ratio,
            }
            if (best_db is None) or (sil > best_db['silhouette']):
                best_db = rec
                cluster_labels['dbscan'] = labels
if best_db is not None:
    rows.append(best_db)

results = pd.DataFrame(rows).sort_values(['silhouette'], ascending=False).reset_index(drop=True)
results.to_csv(out / 'model_comparison.csv', index=False)

best_model = results.iloc[0]['model']
if best_model == 'dbscan':
    top_noise = float(results.iloc[0]['noise_ratio'])
    # DBSCAN is not operationally useful if almost all points are treated as noise.
    if top_noise > 0.40 and len(results) > 1:
        best_model = results.iloc[1]['model']
    elif len(results) > 1 and (results.iloc[0]['silhouette'] - results.iloc[1]['silhouette'] < 0.03):
        best_model = results.iloc[1]['model']

labels = cluster_labels[best_model]
work = df.copy()
work['cluster'] = labels
if best_model == 'dbscan':
    work = work[work['cluster'] != -1].copy()

num_profile = work.groupby('cluster')[num_cols].mean()
cat_profile = work.groupby('cluster')[cat_cols].agg(lambda s: s.mode().iloc[0] if not s.mode().empty else s.iloc[0])
size_profile = work['cluster'].value_counts().sort_index().rename('employees')
profile = pd.concat([size_profile, num_profile, cat_profile], axis=1).reset_index().rename(columns={'index': 'cluster'})

z_means = (num_profile - num_profile.mean()) / (num_profile.std(ddof=0) + 1e-9)
risk = (
    0.25 * z_means['workload_index']
    + 0.25 * z_means['absenteeism_days']
    - 0.20 * z_means['performance_score']
    - 0.15 * z_means['salary_k']
    - 0.15 * z_means['tenure_years']
)
profile = profile.merge(risk.rename('risk_score').reset_index(), on='cluster', how='left')
profile = profile.sort_values('risk_score', ascending=False)
profile.to_csv(out / 'cluster_profiles.csv', index=False)

sns.set_theme(style='whitegrid')
plt.figure(figsize=(8, 5))
ax = sns.barplot(data=profile, x='cluster', y='employees', hue='cluster', palette='Blues_d', legend=False)
ax.set_title(f'Tamano de clusters ({best_model})')
ax.set_xlabel('Cluster')
ax.set_ylabel('Numero de empleados')
plt.tight_layout()
plt.savefig(plots / 'cluster_sizes.png', dpi=150)
plt.close()

plt.figure(figsize=(8, 5))
ax = sns.barplot(data=profile, x='cluster', y='risk_score', hue='cluster', palette='Reds', legend=False)
ax.set_title('Indice de riesgo potencial de fuga por cluster')
ax.set_xlabel('Cluster')
ax.set_ylabel('Risk score (relativo)')
plt.tight_layout()
plt.savefig(plots / 'cluster_risk.png', dpi=150)
plt.close()

median_vals = df[num_cols].median()
actions = []
for _, r in profile.iterrows():
    c = int(r['cluster'])
    recs = []
    if r['workload_index'] > median_vals['workload_index']:
        recs.append('Rebalancear carga y definir tope de workload por equipo (4 semanas).')
    if r['absenteeism_days'] > median_vals['absenteeism_days']:
        recs.append('Programa de bienestar/flexibilidad con seguimiento semanal de ausentismo.')
    if r['salary_k'] < median_vals['salary_k']:
        recs.append('Revision salarial focalizada para percentil bajo del cluster, no masiva.')
    if r['tenure_years'] < median_vals['tenure_years']:
        recs.append('Plan de onboarding extendido y mentoring en primeros 90 dias.')
    if r['performance_score'] > median_vals['performance_score'] and r['salary_k'] < median_vals['salary_k']:
        recs.append('Retention package para alto desempeno con salario rezagado.')
    if not recs:
        recs.append('Mantener politicas actuales y monitorear indicadores mensuales.')

    actions.append({
        'cluster': c,
        'employees': int(r['employees']),
        'risk_score': float(r['risk_score']),
        'top_department': r['Department'],
        'top_education': r['Education_Level'],
        'actions': recs,
    })

actions = sorted(actions, key=lambda x: x['risk_score'], reverse=True)

report_lines = []
report_lines.append('# Plan de accion ejecutado (fuga de empleados)')
report_lines.append('')
report_lines.append('## Resumen ejecutivo')
report_lines.append(f'- Empleados analizados: {len(df)}')
report_lines.append(f"- Variables numericas: {', '.join(num_cols)}")
report_lines.append(f"- Variables categoricas: {', '.join(cat_cols)}")
report_lines.append(f'- PCA recomendado para 95% varianza: {n95} componentes')
report_lines.append('')
report_lines.append('## Comparacion de modelos')
report_lines.append('```text')
report_lines.append(results.to_string(index=False))
report_lines.append('```')
report_lines.append('')
report_lines.append(f'Modelo seleccionado para accion: **{best_model}**')
report_lines.append('')
report_lines.append('## Plan de accion por cluster (priorizado por riesgo)')
for a in actions:
    report_lines.append(f"### Cluster {a['cluster']} | empleados={a['employees']} | risk_score={a['risk_score']:.3f}")
    report_lines.append(f"- Perfil dominante: Department={a['top_department']}, Education_Level={a['top_education']}")
    for rec in a['actions']:
        report_lines.append(f'- {rec}')
    report_lines.append('')

report_lines.append('## KPIs de seguimiento (8-12 semanas)')
report_lines.append('- Reducir ausentismo promedio del cluster de mayor riesgo en >= 10%.')
report_lines.append('- Reducir workload_index promedio del cluster de mayor riesgo en >= 8%.')
report_lines.append('- Mejorar performance_score en clusters intervenidos en >= 3 puntos.')
report_lines.append('- Retencion trimestral del top 20% de riesgo: mejora >= 5 pp.')
report_lines.append('')
report_lines.append('## Archivos generados')
report_lines.append('- outputs/model_comparison.csv')
report_lines.append('- outputs/cluster_profiles.csv')
report_lines.append('- outputs/plots/cluster_sizes.png')
report_lines.append('- outputs/plots/cluster_risk.png')

(out / 'plan_accion.md').write_text('\n'.join(report_lines), encoding='utf-8')

print('OK: plan ejecutado')
print('Modelo seleccionado:', best_model)
print(results[['model', 'k_or_param', 'silhouette', 'noise_ratio']].to_string(index=False))
print('Reporte:', (out / 'plan_accion.md').as_posix())
