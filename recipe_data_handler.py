import pandas as pd
import os

def fetch_filtered_recipes(recipe_name, allergens):
    # Load recipe data from CSV file
    csv_path = os.path.join(os.path.dirname(__file__), 'recipedata.csv')
    try:
        recipe_data = pd.read_csv(csv_path, nrows=300)  # Limiting to 300 rows for performance
        print("Recipe data loaded successfully. Total recipes:", len(recipe_data))
    except FileNotFoundError:
        raise FileNotFoundError("The recipe data file could not be found.")
    
    # Debugging statement to verify data loaded
    print(recipe_data.head())

    # Filter recipes by name if provided
    if recipe_name:
        recipe_data = recipe_data[recipe_data['title'].str.contains(recipe_name, case=False, na=False)]
        print("Recipes after filtering by name:", len(recipe_data))

    # Remove any empty strings from the allergens list
    allergens = [allergen for allergen in allergens if allergen.strip()]
    print("Filtered allergens list:", allergens)

    # Filter out recipes containing any of the selected allergens
    if allergens:
        for allergen in allergens:
            recipe_data = recipe_data[~recipe_data['ingredients'].str.contains(allergen, case=False, na=False)]
            print(f"Recipes after filtering allergen '{allergen}':", len(recipe_data))

    # Convert filtered recipes to a list of dictionaries
    recipes_list = recipe_data.to_dict(orient='records')
    print("Number of recipes passed to the template:", len(recipes_list))
    return recipes_list
