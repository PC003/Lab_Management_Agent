"""Simulated lab data — test catalog, supplies, and sample results.

In a production system these would come from a database.
"""

# Tests available in our lab, grouped by where they can be performed
TEST_CATALOG: dict[str, dict] = {
    "CBC": {
        "name": "Complete Blood Count (CBC)",
        "locations": ["lab", "hospital"],
        "supplies_required": ["EDTA tubes", "blood collection needles", "CBC reagent"],
        "turnaround_hours": 4,
        "price": 500,
    },
    "blood_sugar": {
        "name": "Blood Sugar (Fasting/PP)",
        "locations": ["lab", "home", "hospital"],
        "supplies_required": ["glucose strips", "fluoride tubes", "lancets"],
        "turnaround_hours": 2,
        "price": 200,
    },
    "lipid_profile": {
        "name": "Lipid Profile",
        "locations": ["lab", "hospital"],
        "supplies_required": ["serum tubes", "lipid reagent kit"],
        "turnaround_hours": 6,
        "price": 800,
    },
    "thyroid_profile": {
        "name": "Thyroid Profile (T3, T4, TSH)",
        "locations": ["lab", "hospital"],
        "supplies_required": ["serum tubes", "thyroid assay kit", "ELISA plates"],
        "turnaround_hours": 24,
        "price": 1200,
    },
    "urine_routine": {
        "name": "Urine Routine & Microscopy",
        "locations": ["lab", "home", "hospital"],
        "supplies_required": ["urine container", "dipstick strips", "microscope slides"],
        "turnaround_hours": 3,
        "price": 300,
    },
    "liver_function": {
        "name": "Liver Function Test (LFT)",
        "locations": ["lab", "hospital"],
        "supplies_required": ["serum tubes", "LFT reagent kit"],
        "turnaround_hours": 6,
        "price": 900,
    },
    "kidney_function": {
        "name": "Kidney Function Test (KFT)",
        "locations": ["lab", "hospital"],
        "supplies_required": ["serum tubes", "KFT reagent kit"],
        "turnaround_hours": 6,
        "price": 850,
    },
    "hemoglobin": {
        "name": "Hemoglobin (Hb)",
        "locations": ["lab", "home", "hospital"],
        "supplies_required": ["EDTA tubes", "hemoglobin reagent"],
        "turnaround_hours": 1,
        "price": 150,
    },
    "ESR": {
        "name": "Erythrocyte Sedimentation Rate (ESR)",
        "locations": ["lab", "hospital"],
        "supplies_required": ["ESR tubes", "sodium citrate"],
        "turnaround_hours": 2,
        "price": 200,
    },
    "blood_group": {
        "name": "Blood Grouping & Rh Typing",
        "locations": ["lab", "hospital"],
        "supplies_required": ["EDTA tubes", "anti-A serum", "anti-B serum", "anti-D serum"],
        "turnaround_hours": 1,
        "price": 250,
    },
}

# Current supply inventory (simulated)
SUPPLY_INVENTORY: dict[str, int] = {
    "EDTA tubes": 50,
    "blood collection needles": 100,
    "CBC reagent": 20,
    "glucose strips": 200,
    "fluoride tubes": 30,
    "lancets": 150,
    "serum tubes": 60,
    "lipid reagent kit": 10,
    "thyroid assay kit": 5,
    "ELISA plates": 8,
    "urine container": 100,
    "dipstick strips": 80,
    "microscope slides": 200,
    "LFT reagent kit": 12,
    "KFT reagent kit": 10,
    "hemoglobin reagent": 25,
    "ESR tubes": 40,
    "sodium citrate": 30,
    "anti-A serum": 15,
    "anti-B serum": 15,
    "anti-D serum": 15,
}

# Sample test results for simulation
SAMPLE_RESULTS: dict[str, dict[str, str]] = {
    "CBC": {
        "WBC": "7,500 /cumm (Normal: 4,000-11,000)",
        "RBC": "4.8 million/cumm (Normal: 4.5-5.5)",
        "Hemoglobin": "13.5 g/dL (Normal: 12-16)",
        "Hematocrit": "42% (Normal: 36-46)",
        "Platelet Count": "2,50,000 /cumm (Normal: 1,50,000-4,00,000)",
        "MCV": "88 fL (Normal: 80-100)",
        "MCH": "28 pg (Normal: 27-31)",
    },
    "blood_sugar": {
        "Fasting Blood Sugar": "95 mg/dL (Normal: 70-100)",
        "Post Prandial": "130 mg/dL (Normal: <140)",
    },
    "lipid_profile": {
        "Total Cholesterol": "195 mg/dL (Desirable: <200)",
        "HDL": "52 mg/dL (Normal: >40)",
        "LDL": "118 mg/dL (Optimal: <100)",
        "Triglycerides": "145 mg/dL (Normal: <150)",
        "VLDL": "29 mg/dL (Normal: 5-40)",
    },
    "thyroid_profile": {
        "T3": "1.2 ng/mL (Normal: 0.8-2.0)",
        "T4": "7.8 mcg/dL (Normal: 5.1-14.1)",
        "TSH": "3.2 mIU/L (Normal: 0.4-4.0)",
    },
    "urine_routine": {
        "Color": "Pale Yellow",
        "pH": "6.0 (Normal: 4.5-8.0)",
        "Specific Gravity": "1.020 (Normal: 1.005-1.030)",
        "Protein": "Nil",
        "Sugar": "Nil",
        "Pus Cells": "2-3 /hpf (Normal: 0-5)",
        "RBC": "Nil",
    },
    "liver_function": {
        "Total Bilirubin": "0.8 mg/dL (Normal: 0.1-1.2)",
        "Direct Bilirubin": "0.2 mg/dL (Normal: 0-0.3)",
        "SGOT (AST)": "28 U/L (Normal: 5-40)",
        "SGPT (ALT)": "32 U/L (Normal: 7-56)",
        "Alkaline Phosphatase": "75 U/L (Normal: 44-147)",
        "Total Protein": "7.2 g/dL (Normal: 6.0-8.3)",
        "Albumin": "4.0 g/dL (Normal: 3.5-5.5)",
    },
    "kidney_function": {
        "Blood Urea": "30 mg/dL (Normal: 15-40)",
        "Serum Creatinine": "0.9 mg/dL (Normal: 0.7-1.3)",
        "Uric Acid": "5.5 mg/dL (Normal: 3.5-7.2)",
        "BUN": "14 mg/dL (Normal: 7-20)",
    },
    "hemoglobin": {
        "Hemoglobin": "13.2 g/dL (Normal: 12-16)",
    },
    "ESR": {
        "ESR (Westergren)": "12 mm/hr (Normal: 0-20)",
    },
    "blood_group": {
        "Blood Group": "B Positive (B+)",
        "Rh Factor": "Positive",
    },
}


def get_available_tests(location: str | None = None) -> list[dict]:
    """Return tests available at the given location (or all if not specified)."""
    results = []
    for key, test in TEST_CATALOG.items():
        if location is None or location in test["locations"]:
            results.append({"id": key, **test})
    return results


def check_supplies(test_id: str) -> dict:
    """Check if we have the supplies needed for a given test.

    Returns a dict with:
      - available: bool — whether all supplies are in stock
      - missing: list[str] — any supplies that are out of stock
    """
    test = TEST_CATALOG.get(test_id)
    if not test:
        return {"available": False, "missing": [], "error": f"Unknown test: {test_id}"}

    missing = [
        supply
        for supply in test["supplies_required"]
        if SUPPLY_INVENTORY.get(supply, 0) <= 0
    ]
    return {"available": len(missing) == 0, "missing": missing}


def get_test_results(test_id: str) -> dict[str, str] | None:
    """Simulate running a lab test and return results."""
    return SAMPLE_RESULTS.get(test_id)
