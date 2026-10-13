"""
Profile Module
Responsible for validating patient demographic parameters (Age, Sex)
and establishing baseline clinical risk categories (Pediatric, Adult, Geriatric).
"""
from typing import Dict, Any, Tuple, Optional


class ProfileModule:
    @staticmethod
    def validate_and_create_profile(age_raw: Any, sex: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Validates age as a valid positive integer within clinical human limits (0 - 120).
        Assigns clinical demographic grouping.
        """
        try:
            # Handle float strings like '22.0' or plain strings '22'
            age_float = float(str(age_raw).strip())
            age = int(age_float)
            if age_float != age and age_float < 1:
                # e.g., infant months expressed as 0.5
                age = round(age_float, 1)
        except (ValueError, TypeError):
            return False, None, "Age must be a valid numeric value."

        if age < 0 or age > 125:
            return False, None, "Please enter a realistic age between 0 and 125 years."

        # Demographic category for clinical context
        if age < 18:
            demographic_group = "Pediatric"
        elif age >= 65:
            demographic_group = "Geriatric"
        else:
            demographic_group = "Adult"

        profile = {
            "age": age,
            "sex": sex if sex in ["Male", "Female", "Other"] else "Other",
            "demographic_group": demographic_group,
            "clinical_notes": f"{demographic_group} individual ({age} years old, {sex})"
        }

        return True, profile, None
