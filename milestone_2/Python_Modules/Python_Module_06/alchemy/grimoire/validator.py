def validate_ingredients(ingredients: str) -> str:
    valid_terms = ("fire", "water", "earth", "air")

    if any(term in ingredients for term in valid_terms):
        return f"{ingredients} - VALID"
    return f"{ingredients} - INVALID"
