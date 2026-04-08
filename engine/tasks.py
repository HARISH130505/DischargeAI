from .models import PatientInfo

TASKS = {
    "EASY": {
        "patient_info": PatientInfo(
            age=45,
            condition="Post-appendectomy, recovering well",
            vitals="Stable (HR 72, BP 115/75, Temp 37.0C)",
            mobility="Independent, walking with minimal pain",
            home_support="Spouse at home, full support available",
            risk_level="Low"
        ),
        "ideal_action": "discharge",
        "description": "Patient is stable and ready for discharge with simple follow-up."
    },
    "MEDIUM": {
        "patient_info": PatientInfo(
            age=72,
            condition="Recent hip replacement, day 3 post-op",
            vitals="Stable (HR 80, BP 130/85, Temp 37.1C)",
            mobility="Requires walker and standby assist, high fall risk",
            home_support="Lives alone, family can visit 3x a week",
            risk_level="Medium"
        ),
        "ideal_action": "refer", # to rehab or SNF
        "description": "Patient is medically stable but unsuited for home environment."
    },
    "HARD": {
        "patient_info": PatientInfo(
            age=68,
            condition="Exacerbation of COPD, resolved but fragile",
            vitals="Borderline (HR 92, BP 145/90, SpO2 93% on room air)",
            mobility="Gets short of breath walking longer than 20 feet",
            home_support="Poor home support, lives in 2nd floor apartment with no elevator",
            risk_level="High"
        ),
        "ideal_action": "keep", # Needs observation delayed discharge to ensure SpO2 stabilization
        "description": "Patient has conflicting health signals requiring monitoring."
    }
}
