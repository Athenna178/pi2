import pandas as pd
import numpy as np

print("Génération des données ITR en cours...")

# 1. Données des actifs (Assets)
assets = pd.DataFrame({
    "counterparty_id": [f"CP_{i}" for i in range(1, 101)],
    "sector": np.random.choice(["Energy", "Tech", "Finance", "Healthcare", "Materials", "Industrials"], 100),
    "asset_class": np.random.choice(["Listed Equity", "Corporate Bonds", "Corporate Loans"], 100),
    "exposure": np.random.uniform(10000, 500000, 100),
    "weight": np.random.uniform(0.001, 0.05, 100),
    "current_intensity": np.random.uniform(50, 500, 100),
    "reduction_rate": np.random.uniform(0.01, 0.08, 100),
    "source": np.random.choice(["SBTi Target", "Sector Proxy", "Broad Default"], 100, p=[0.4, 0.4, 0.2]),
    "itr": np.random.uniform(1.2, 4.5, 100),
    "dqs": np.random.choice([1, 2, 3, 4, 5], 100),
    "outlier_flag": np.random.choice([False, True], 100, p=[0.9, 0.1])
})
assets.to_csv("itr_assets_data.csv", sep=";", index=False)

# 2. Données sectorielles
sector = assets.groupby("sector")["itr"].mean().reset_index()
sector.to_csv("itr_sector_indicator.csv", sep=";", index=False)

# 3. Données par classe d'actifs
asset_class = assets.groupby("asset_class")["itr"].mean().reset_index()
asset_class.to_csv("itr_asset_class_indicator.csv", sep=";", index=False)

# 4. Métriques de couverture
coverage = assets["source"].value_counts(normalize=True).reset_index()
coverage.columns = ["source", "percentage"]
coverage["percentage"] *= 100
coverage.to_csv("itr_coverage_metrics.csv", sep=";", index=False)

# 5. Résumé du portefeuille (KPIs)
summary = pd.DataFrame({
    "metric": ["portfolio_itr", "scenario_baseline", "weighted_dqs"],
    "value": [2.35, 1.5, 2.8]
})
summary.to_csv("itr_summary.csv", sep=";", index=False)

print("✅ Fichiers CSV générés avec succès !")