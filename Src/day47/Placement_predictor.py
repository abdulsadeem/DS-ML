# ================================
# IMPORTS
# ================================
import numpy as np
import time

from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

# ================================
# PHASE 1: DATA ARCHITECTURE
# ================================

# Generate dataset
X, y = make_classification(
    n_samples=1000,
    n_features=20,
    n_informative=10,
    n_redundant=5,
    n_classes=2,
    weights=[0.9, 0.1],  # Imbalanced dataset
    random_state=42
)

# Train-test split (80/20)
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

# Feature scaling (avoid data leakage)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ================================
# PHASE 2: BASELINE MODEL
# ================================

rf = RandomForestClassifier(random_state=42)
rf.fit(X_train_scaled, y_train)

y_pred = rf.predict(X_test_scaled)

baseline_acc = accuracy_score(y_test, y_pred)
baseline_f1 = f1_score(y_test, y_pred)

print("===== BASELINE MODEL =====")
print("Accuracy:", baseline_acc)
print("F1 Score:", baseline_f1)

# ================================
# GRID SEARCH SETUP
# ================================

param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5, 10]
}

# ================================
# GRID SEARCH (ACCURACY)
# ================================

grid_acc = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid=param_grid,
    scoring='accuracy',
    cv=5,
    n_jobs=-1
)

grid_acc.fit(X_train_scaled, y_train)

print("\n===== GRID SEARCH (ACCURACY) =====")
print("Best Params:", grid_acc.best_params_)

# ================================
# GRID SEARCH (F1 SCORE)
# ================================

grid_f1 = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid=param_grid,
    scoring='f1',
    cv=5,
    n_jobs=-1
)

start_grid = time.time()
grid_f1.fit(X_train_scaled, y_train)
grid_time = time.time() - start_grid

print("\n===== GRID SEARCH (F1) =====")
print("Best Params:", grid_f1.best_params_)

# Evaluate Grid Best Model
grid_best = grid_f1.best_estimator_
grid_pred = grid_best.predict(X_test_scaled)

grid_test_f1 = f1_score(y_test, grid_pred)

# ================================
# RANDOMIZED SEARCH
# ================================

param_dist = {
    'n_estimators': np.arange(10, 500),
    'max_depth': [None] + list(np.arange(5, 30)),
    'min_samples_split': np.arange(2, 20)
}

random_search = RandomizedSearchCV(
    RandomForestClassifier(random_state=42),
    param_distributions=param_dist,
    n_iter=20,
    scoring='f1',
    cv=5,
    random_state=42,
    n_jobs=-1
)

start_random = time.time()
random_search.fit(X_train_scaled, y_train)
random_time = time.time() - start_random

print("\n===== RANDOMIZED SEARCH =====")
print("Best Params:", random_search.best_params_)

# Evaluate Random Best Model
random_best = random_search.best_estimator_
random_pred = random_best.predict(X_test_scaled)

random_test_f1 = f1_score(y_test, random_pred)

# ================================
# FINAL COMPARISON TABLE
# ================================

print("\n===== FINAL COMPARISON =====")
print("--------------------------------------------------")
print(f"Baseline        | Acc: {baseline_acc:.4f} | F1: {baseline_f1:.4f}")
print(f"Grid Search     | Time: {grid_time:.2f}s | F1: {grid_test_f1:.4f}")
print(f"Random Search   | Time: {random_time:.2f}s | F1: {random_test_f1:.4f}")
print("--------------------------------------------------")