"""
PROJECT: University Placement Predictor (Random Forest Optimization)
GOAL: Compare GridSearchCV vs. RandomizedSearchCV on Imbalanced Data
"""

import time
import numpy as np
import pandas as pd
from scipy.stats import randint
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, f1_score, accuracy_score

# ==========================================
# 1. DATA PREPARATION
# ==========================================
print("--- Step 1: Generating Imbalanced Placement Data ---")
# 1000 students, 20 features, 10% unplaced (Class 1)
X, y = make_classification(
    n_samples=1000, n_features=20, n_informative=15, 
    n_redundant=5, weights=[0.9, 0.1], random_state=42
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# SCALING: Fit on Train ONLY to prevent Data Leakage
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ==========================================
# 2. BASELINE MODEL
# ==========================================
print("\n--- Step 2: Training Baseline (Default Params) ---")
baseline = RandomForestClassifier(random_state=42)
baseline.fit(X_train_scaled, y_train)
y_pred = baseline.predict(X_test_scaled)

print(f"Baseline Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"Baseline F1-Score: {f1_score(y_test, y_pred):.4f}")

# ==========================================
# 3. EXHAUSTIVE GRID SEARCH (F1-OPTIMIZED)
# ==========================================
print("\n--- Step 3: Running Grid Search (F1-Score) ---")
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10]
}

grid_search = GridSearchCV(
    estimator=RandomForestClassifier(random_state=42),
    param_grid=param_grid,
    cv=5,
    scoring='f1',
    n_jobs=-1 # Using all CPU cores
)

start_grid = time.time()
grid_search.fit(X_train_scaled, y_train)
end_grid = time.time()

grid_time = end_grid - start_grid
print(f"Grid Search Time: {grid_time:.2f} seconds")
print(f"Best Params (Grid): {grid_search.best_params_}")

# ==========================================
# 4. RANDOMIZED SEARCH EFFICIENCY
# ==========================================
print("\n--- Step 4: Running Randomized Search (Wider Range) ---")
param_dist = {
    'n_estimators': randint(10, 500),
    'max_depth': [None, 10, 20, 30, 40, 50],
    'min_samples_split': randint(2, 20)
}

random_search = RandomizedSearchCV(
    estimator=RandomForestClassifier(random_state=42),
    param_distributions=param_dist,
    n_iter=20, # Fixed number of iterations
    cv=5,
    scoring='f1',
    random_state=42,
    n_jobs=-1
)

start_rand = time.time()
random_search.fit(X_train_scaled, y_train)
end_rand = time.time()

rand_time = end_rand - start_rand
print(f"Random Search Time: {rand_time:.2f} seconds")
print(f"Best Params (Random): {random_search.best_params_}")

# ==========================================
# 5. FINAL COMPARISON & METRIC ANALYSIS
# ==========================================
print("\n" + "="*40)
print("FINAL PERFORMANCE COMPARISON")
print("="*40)

# Evaluate Best Grid Model
grid_final_pred = grid_search.predict(X_test_scaled)
# Evaluate Best Random Model
rand_final_pred = random_search.predict(X_test_scaled)

print(f"Grid Search F1:   {f1_score(y_test, grid_final_pred):.4f} | Time: {grid_time:.2f}s")
print(f"Random Search F1: {f1_score(y_test, rand_final_pred):.4f} | Time: {rand_time:.2f}s")

print("\nMENTOR'S NOTE ON THE 'METRIC TRAP':")
print("> If we optimized for 'Accuracy', the model might ignore the minority class.")
print("> F1-Score ensures we identify the students who actually need help.")