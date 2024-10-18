import re
from dataclasses import dataclass

@dataclass
class ParsedIngredient:
    ingredient_text: str
    name: str
    quantity: str = None
    unit: str = None

def parse_multiple_ingredients(ingredient_lines):
    parsed_ingredients = []
    for line in ingredient_lines:
        parsed_ingredient = parse_ingredient(line)
        # Only add the ingredient if the name is not empty
        if parsed_ingredient.name:
            parsed_ingredients.append(parsed_ingredient)
    
    # Create a list with only the ingredient names for the 'NER' field
    ner_list = [ingredient.name for ingredient in parsed_ingredients if ingredient.name]

    # Return the formatted recipe dictionary and parsed ingredients
    parsed_recipe = {
        'title': 'Custom Recipe',
        'directions': 'Step 1: Mix all ingredients. Step 2: Cook as required.',  # Placeholder directions
        'NER': ', '.join(ner_list),
        'ingredients': ', '.join([f"{ing.quantity or ''} {ing.unit or ''} {ing.name}".strip() for ing in parsed_ingredients])
    }

    # Debug print statements
    print("Parsed Ingredients List:", parsed_ingredients)
    print("Formatted Recipe Dictionary:", parsed_recipe)

    return parsed_recipe, parsed_ingredients

def parse_ingredient(ingredient_text):
    # Simple parsing logic
    pattern = r'(?P<quantity>\d*\.?\d+)?\s*(?P<unit>\w+)?\s*(?P<name>.+)'
    match = re.match(pattern, ingredient_text)
    print(ingredient_text)
    if match:
        return ParsedIngredient(
            ingredient_text,
            name=match.group('name').strip() if match.group('name') else '',
            quantity=match.group('quantity'),
            unit=match.group('unit')
        )
    else:
        return ParsedIngredient(name=ingredient_text.strip())
