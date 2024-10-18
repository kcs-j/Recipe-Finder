import requests
from functools import lru_cache

@lru_cache(maxsize=100)
def fetch_ingredient_data(ingredient_name, limit=5):
    base_url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": ingredient_name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": limit  # Limit the number of results to fetch
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        products = data.get("products", [])
        # Process products to keep only relevant data
        cleaned_products = []
        for product in products:
            cleaned_product = {
                'product_name': product.get('product_name'),
                'image_url': product.get('image_url'),
                'nutrients': extract_nutrients(product),
                'code': product.get('code'),
                'brands': product.get('brands'),
                'allergens_hierarchy': product.get('allergens_hierarchy'),
                'serving_size': product.get('serving_size'),  # Extract serving size
            }
            cleaned_products.append(cleaned_product)
        return cleaned_products
    except requests.exceptions.RequestException as e:
        print(f"API Request error: {e}")
        return []
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
        return []

def extract_nutrients(product):
    # Define the nutrients you want to extract
    nutrients_wanted = [
        'energy-kcal',
        'fat',
        'saturated-fat',
        'carbohydrates',
        'sugars',
        'fiber',
        'proteins',
        'salt',
        'sodium'
    ]
    nutrients_data = product.get('nutriments', {})
    nutrients_list = []
    for nutrient in nutrients_wanted:
        # Try to get per serving values first
        amount = nutrients_data.get(f"{nutrient}_serving")
        unit = nutrients_data.get(f"{nutrient}_unit")
        per_100g = nutrients_data.get(f"{nutrient}_100g")

        # If per serving amount is not available, fall back to per 100g
        if amount is None:
            amount = per_100g
            if amount is not None:
                # We'll handle the quantity scaling in the nutrition calculator
                per_100g_available = True
            else:
                per_100g_available = False
        else:
            per_100g_available = False  # We're using per serving values

        if amount is not None:
            nutrient_name = nutrient.replace('-', ' ').title()
            nutrients_list.append({
                'name': nutrient_name,
                'amount': amount,
                'unit': unit or '',
                'per_100g_available': per_100g_available
            })
    return nutrients_list

if __name__ == "__main__":
    # Test the function with an example ingredient
    ingredient = "sugar"
    products = fetch_ingredient_data(ingredient)
    for product in products:
        print(product)
