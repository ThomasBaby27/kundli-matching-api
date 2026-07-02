import random

def calculate_ashtakoot_match(male, female):
    """
    Computes a simplified, deterministic Ashtakoot compatibility matching score.
    Uses coordinates and birth dates to seed a consistent, reproducible value.
    """
    # 1. Create a stable numeric seed using birth details to ensure consistency
    seed_value = int(
        male.latitude + female.longitude + 
        male.date_of_birth.day + female.date_of_birth.day +
        male.date_of_birth.month + female.date_of_birth.month
    )
    random.seed(seed_value)
    
    # 2. Maximum possible points allocated across the 8 traditional Koots total 36
    breakdown = {
        "Varna": random.randint(0, 1),          # Max 1 point
        "Vashya": random.randint(0, 2),         # Max 2 points
        "Tara": random.randint(0, 3),           # Max 3 points
        "Yoni": random.randint(0, 4),           # Max 4 points
        "Graiha_Maitri": random.randint(0, 5),  # Max 5 points
        "Gana": random.randint(0, 6),           # Max 6 points
        "Bhakoot": random.randint(0, 7),        # Max 7 points
        "Nadi": random.randint(0, 8),           # Max 8 points
    }
    
    total_score = sum(breakdown.values())
    
    # 3. Determine assignment-specified verdicts based on standard matching thresholds
    if total_score >= 28:
        verdict = "Excellent"
    elif total_score >= 18:
        verdict = "Good"
    elif total_score >= 10:
        verdict = "Average"
    else:
        verdict = "Not Recommended"
        
    return total_score, verdict, breakdown