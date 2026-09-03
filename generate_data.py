"""
Generates a synthetic multi-line (auto + home) insurance policy dataset.
Designed to have realistic, discoverable premium drivers so SQL analysis
turns up meaningful patterns (not pure noise).
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N_CUSTOMERS = 800

states = ["CT", "MA", "NY", "NJ", "RI", "PA"]
credit_tiers = ["Excellent", "Good", "Fair", "Poor"]
credit_weights = [0.25, 0.35, 0.25, 0.15]

# ---------- Customers ----------
customer_ids = np.arange(1, N_CUSTOMERS + 1)
ages = rng.integers(18, 80, N_CUSTOMERS)
state = rng.choice(states, N_CUSTOMERS)
credit_tier = rng.choice(credit_tiers, N_CUSTOMERS, p=credit_weights)
years_with_company = rng.integers(0, 20, N_CUSTOMERS)
prior_claims_5yr = rng.poisson(0.4, N_CUSTOMERS).clip(0, 5)
bundled = rng.choice([0, 1], N_CUSTOMERS, p=[0.55, 0.45])  # has both auto+home

customers = pd.DataFrame({
    "customer_id": customer_ids,
    "age": ages,
    "state": state,
    "credit_tier": credit_tier,
    "years_with_company": years_with_company,
    "prior_claims_5yr": prior_claims_5yr,
    "bundled_discount": bundled,
})

credit_multiplier = {"Excellent": 0.85, "Good": 1.0, "Fair": 1.15, "Poor": 1.35}
state_multiplier = {"CT": 1.05, "MA": 1.10, "NY": 1.20, "NJ": 1.15, "RI": 1.0, "PA": 0.95}

# ---------- Auto policies ----------
auto_rows = []
vehicle_types = ["Sedan", "SUV", "Truck", "Coupe", "Minivan"]
coverage_levels = ["Liability Only", "Standard", "Full Coverage"]
coverage_base = {"Liability Only": 550, "Standard": 900, "Full Coverage": 1400}

n_auto = int(N_CUSTOMERS * 0.85)
auto_customers = rng.choice(customer_ids, n_auto, replace=False)

for cid in auto_customers:
    cust = customers.loc[customers.customer_id == cid].iloc[0]
    vtype = rng.choice(vehicle_types, p=[0.35, 0.30, 0.12, 0.13, 0.10])
    coverage = rng.choice(coverage_levels, p=[0.25, 0.45, 0.30])
    base = coverage_base[coverage]

    age_factor = 1.4 if cust.age < 25 else (1.15 if cust.age < 30 else (0.95 if cust.age < 65 else 1.05))
    vehicle_factor = {"Sedan": 1.0, "SUV": 1.08, "Truck": 1.12, "Coupe": 1.20, "Minivan": 0.95}[vtype]
    claims_factor = 1 + (cust.prior_claims_5yr * 0.12)
    tenure_discount = max(0.85, 1 - cust.years_with_company * 0.01)
    bundle_discount = 0.90 if cust.bundled_discount else 1.0

    premium = (base * age_factor * vehicle_factor * claims_factor
               * credit_multiplier[cust.credit_tier] * state_multiplier[cust.state]
               * tenure_discount * bundle_discount)
    premium *= rng.normal(1.0, 0.05)  # noise

    auto_rows.append({
        "policy_id": f"A{cid:04d}",
        "customer_id": cid,
        "policy_type": "Auto",
        "vehicle_type": vtype,
        "coverage_level": coverage,
        "annual_premium": round(max(premium, 200), 2),
    })

auto_df = pd.DataFrame(auto_rows)

# ---------- Home policies ----------
home_rows = []
home_types = ["Single Family", "Condo", "Townhouse", "Multi-Family"]
coverage_home_base = {"Liability Only": 400, "Standard": 800, "Full Coverage": 1300}

n_home = int(N_CUSTOMERS * 0.65)
home_customers = rng.choice(customer_ids, n_home, replace=False)

for cid in home_customers:
    cust = customers.loc[customers.customer_id == cid].iloc[0]
    htype = rng.choice(home_types, p=[0.5, 0.2, 0.2, 0.1])
    coverage = rng.choice(coverage_levels, p=[0.15, 0.45, 0.40])
    base = coverage_home_base[coverage]

    home_value_factor = rng.uniform(0.85, 1.6)
    home_type_factor = {"Single Family": 1.05, "Condo": 0.85, "Townhouse": 0.95, "Multi-Family": 1.20}[htype]
    claims_factor = 1 + (cust.prior_claims_5yr * 0.10)
    tenure_discount = max(0.88, 1 - cust.years_with_company * 0.008)
    bundle_discount = 0.92 if cust.bundled_discount else 1.0

    premium = (base * home_value_factor * home_type_factor * claims_factor
               * credit_multiplier[cust.credit_tier] * state_multiplier[cust.state]
               * tenure_discount * bundle_discount)
    premium *= rng.normal(1.0, 0.05)

    home_rows.append({
        "policy_id": f"H{cid:04d}",
        "customer_id": cid,
        "policy_type": "Home",
        "home_type": htype,
        "coverage_level": coverage,
        "annual_premium": round(max(premium, 200), 2),
    })

home_df = pd.DataFrame(home_rows)

customers.to_csv("customers.csv", index=False)
auto_df.to_csv("auto_policies.csv", index=False)
home_df.to_csv("home_policies.csv", index=False)

print(f"customers: {len(customers)}, auto policies: {len(auto_df)}, home policies: {len(home_df)}")
