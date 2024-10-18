from utils import convert_to_grams

def calculate_nutrition(selected_products):
    """
    Calculates the total nutrition of the recipe based on selected products.
    """
    # Initialize total nutrients
    total_nutrients = {}

    # Define the nutrients you want to calculate
    nutrients_wanted = [
        'Energy',
        'Fat',
        'Saturated Fat',
        'Carbohydrates',
        'Sugars',
        'Fiber',
        'Proteins',
        'Salt',
        'Sodium'
    ]

    for ingredient_name, product_data in selected_products.items():
        print(f"Processing ingredient: {ingredient_name}")  # Debugging statement
        print(f"Product data: {product_data}")  # Debugging statement

        # Get the quantity and unit for the ingredient
        quantity = product_data.get('quantity', None)  # User-specified quantity
        unit = product_data.get('unit', None)          # User-specified unit

        # If user hasn't specified quantity, use serving size or default to 100g
        if quantity is None or unit is None:
            serving_size = product_data.get('serving_size', '100g')
            # Parse serving size into quantity and unit
            quantity, unit = parse_serving_size(serving_size)
            if quantity is None or unit is None:
                print(f"Could not determine serving size for '{ingredient_name}'. Skipping.")
                continue

        # Convert quantity to grams
        quantity_in_grams = convert_to_grams(quantity, unit)
        if quantity_in_grams is None:
            print(f"Could not convert quantity for '{ingredient_name}'. Skipping.")
            continue

        # Get the nutrient data
        nutrients = product_data.get('nutrients', [])

        # Calculate nutrient values based on available data
        for nutrient_info in nutrients:
            nutrient_name = nutrient_info['name']
            if nutrient_name in nutrients_wanted:
                amount = nutrient_info['amount']
                unit_nutrient = nutrient_info['unit']
                per_100g_available = nutrient_info.get('per_100g_available', False)

                if per_100g_available:
                    # Calculate nutrient amount based on quantity in grams
                    total_amount = (amount * quantity_in_grams) / 100
                else:
                    # Nutrient amount is per serving, scale according to user's quantity
                    # Assuming user's quantity matches the serving size
                    total_amount = amount * (quantity_in_grams / quantity_in_grams)  # Simplifies to amount

                # Add to total nutrients
                if nutrient_name in total_nutrients:
                    total_nutrients[nutrient_name]['amount'] += total_amount
                else:
                    total_nutrients[nutrient_name] = {
                        'amount': total_amount,
                        'unit': unit_nutrient
                    }
                print(f"Nutrient: {nutrient_name}, Total Amount: {total_amount}, Unit: {unit_nutrient}")  # Debugging statement

            print("Total Nutrients:", total_nutrients)  # Debugging statement
            
    # Return the total nutrients dictionary
    return total_nutrients

def parse_serving_size(serving_size_str):
    """
    Parses the serving size string into quantity and unit.
    """
    import re
    # Example serving_size_str: "30g", "1 cup (240ml)", "2 pieces (50g)"
    match = re.match(r'([\d\.]+)\s*([a-zA-Z]+)', serving_size_str)
    if match:
        quantity = float(match.group(1))
        unit = match.group(2)
        return quantity, unit
    else:
        # Handle complex serving sizes if necessary
        print(f"Could not parse serving size: {serving_size_str}")
        return None, None
