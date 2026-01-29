import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

# --- 1. GENERATE SYNTHETIC TRAINING DATA ---
# We simulate two types of behavior:
# Type 0: Normal User (Low frequency, few failures)
# Type 1: Attacker (High frequency, many failures)

print("generating synthetic data...")

# Create 1000 "Normal" samples
normal_data = pd.DataFrame({
    'login_rate': np.random.randint(1, 5, 1000),      # 1-5 attempts per minute
    'failure_rate': np.random.randint(0, 2, 1000),    # 0-1 failures usually
    'label': 0
})

# Create 1000 "Attack" samples
attack_data = pd.DataFrame({
    'login_rate': np.random.randint(10, 100, 1000),   # 10-100 attempts per minute
    'failure_rate': np.random.randint(5, 100, 1000),  # High failure count
    'label': 1
})

# Combine and shuffle
data = pd.concat([normal_data, attack_data]).sample(frac=1).reset_index(drop=True)

# --- 2. TRAIN THE MODEL ---
X = data[['login_rate', 'failure_rate']]
y = data['label']

print("Training Random Forest Model...")
clf = RandomForestClassifier(n_estimators=100)
clf.fit(X, y)

# --- 3. SAVE THE MODEL ---
joblib.dump(clf, 'guard_dog_model.pkl')
print("✅ Model saved as 'guard_dog_model.pkl'")