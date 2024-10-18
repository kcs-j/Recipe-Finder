# allergen_checker.py

def check_allergens(selected_products, selected_allergens):
    """
    Checks the selected products for allergens based on the user's selected allergens.
    """
    allergens_in_recipe = set()
    user_allergens_set = set(a.lower() for a in selected_allergens)
    
    print("Selected products:", selected_products)
    print("User selected allergens:", user_allergens_set)
    print("\nSelected products:")
    for ingredient_name, product in selected_products.items():
        print(f"Ingredient: {ingredient_name}")
        print(f"Product: {product}")
    
    # Mapping of allergens to potential keywords in product names or nutrient names
    allergen_keywords = {
        'milk': ['milk', 'lactose', 'casein', 'whey', 'dairy'],
        'egg': ['egg', 'albumin', 'egg white', 'egg yolk'],
        'peanut': ['peanut'],
        'tree nut': ['almond', 'walnut', 'cashew', 'hazelnut', 'pistachio', 'pecan', 'macadamia', 'brazil nut', 'nut'],
        'fish': ['fish', 'cod', 'salmon', 'tuna', 'trout', 'anchovy', 'bass', 'catfish'],
        'shellfish': ['shrimp', 'crab', 'lobster', 'shellfish', 'mussel', 'oyster', 'scallop', 'prawn'],
        'wheat': ['wheat', 'gluten', 'farina', 'semolina', 'spelt', 'durum'],
        'soy': ['soy', 'soya', 'soybean', 'edamame'],
        'sesame': ['sesame', 'tahini'],
        'gluten': ['gluten', 'wheat', 'barley', 'rye', 'spelt', 'triticale', 'farina', 'semolina'],
        # Add more allergens and keywords as needed
    }

    for ingredient_name, product in selected_products.items():
        print(f"\nProcessing ingredient: {ingredient_name}")
        allergens_in_product = set()
        # Check if product is from Open Food Facts
        if 'allergens_hierarchy' in product:
            print("Product is from Open Food Facts.")
            # Open Food Facts product
            allergens = product.get('allergens_hierarchy', [])
            # Extract allergen names from the hierarchy (e.g., 'en:milk' -> 'milk')
            allergens_in_product.update([a.lower().split(':')[-1] for a in allergens])
            print(f"Allergens in product: {allergens_in_product}")
        else:
            print("Product is from local database.")
            # Local database product
            # Check 'product_name' and 'nutrients' names for allergen keywords
            product_name = product.get('product_name', '').lower()
            print(f"Product name: {product_name}")
            nutrients = product.get('nutrients', [])
            nutrient_names = [nutrient['name'].lower() for nutrient in nutrients]
            print(f"Nutrient names: {nutrient_names}")
            
            for allergen in user_allergens_set:
                keywords = allergen_keywords.get(allergen, [allergen])
                print(f"\nChecking for allergen: {allergen}")
                print(f"Keywords: {keywords}")
                keyword_found = False
                for keyword in keywords:
                    # Check if keyword is in product name
                    if keyword in product_name:
                        print(f"Keyword '{keyword}' found in product name.")
                        allergens_in_product.add(allergen)
                        keyword_found = True
                        break  # Stop checking after finding a match for this allergen
                    # Check if keyword is in any nutrient name
                    elif any(keyword in nutrient_name for nutrient_name in nutrient_names):
                        print(f"Keyword '{keyword}' found in nutrient names.")
                        allergens_in_product.add(allergen)
                        keyword_found = True
                        break  # Stop checking after finding a match for this allergen
                if not keyword_found:
                    print(f"No keywords found for allergen '{allergen}' in this product.")
            
        # Compare with user's selected allergens
        common_allergens = user_allergens_set & allergens_in_product
        if common_allergens:
            print(f"Common allergens found in product: {common_allergens}")
            allergens_in_recipe.update(common_allergens)
        else:
            print("No common allergens found in product.")
    
    print(f"\nAllergens found in recipe: {allergens_in_recipe}")
    return list(allergens_in_recipe)
