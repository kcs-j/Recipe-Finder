from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from recipe_data_handler import fetch_filtered_recipes
from api_requests import fetch_ingredient_data
import os
from recipe_parser import parse_multiple_ingredients
from fetch_from_localdb import fetch_from_localdb
from allergen_checker import check_allergens 
from nutrition_calculator import calculate_nutrition 
from nutrition_calculator import calculate_nutrition
from environmental_impact import calculate_environmental_impact
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/custom_recipe', methods=['POST'])
def custom_recipe():
    # Get the custom recipe text and allergens from the JSON data
    data = request.get_json()
    recipe_text = data.get('recipe', '')
    allergens = data.get('allergens', [])
    allergens = [allergen.strip() for allergen in allergens if allergen.strip()]  # Clean up allergens list

    # Store allergens in the session
    session['allergens'] = allergens

    # Split the recipe input by line and parse ingredients
    ingredient_lines = recipe_text.strip().split('\n')
    parsed_recipe, parsed_ingredients = parse_multiple_ingredients(ingredient_lines)

    # Create a combined list for consistency with existing template
    combined_list = []
    for ingredient in parsed_ingredients:
        combined_list.append({
            'ingredient_text': ingredient.ingredient_text,
            'name': ingredient.name,
            'quantity': ingredient.quantity,
            'unit': ingredient.unit,
        })

    # Render the recipe details page with the custom recipe and combined list
    return render_template('recipe_details.html', recipe=parsed_recipe, is_custom=True, allergens=allergens, combined_list=combined_list)




@app.route('/search', methods=['POST'])
def search():
    recipe_name = request.form.get('recipe')
    allergens = request.form.get('allergens', '').split(',')
    # Store allergens in the session
    session['allergens'] = allergens
    filtered_recipes = fetch_filtered_recipes(recipe_name, allergens)
    return render_template('results.html', recipes=filtered_recipes, allergens=allergens)

@app.route('/recipe_details/<recipe_title>', methods=['GET', 'POST'])
def recipe_details(recipe_title):
    if request.method == 'POST':
        # Get updated allergens from the form data
        allergens = request.form.get('allergens', '')
        allergens = allergens.split(',') if allergens else []
        # Store allergens in the session
        session['allergens'] = allergens
    else:
        # Retrieve allergens from the session
        allergens = session.get('allergens', [])
    
    # Fetch the recipe, applying allergen filters if necessary
    recipe = next((r for r in fetch_filtered_recipes('', allergens) if r['title'] == recipe_title), None)

     # Create the combined list for use in the template
    ingredients = recipe.get('ingredients', '').strip('[]').replace('"', '').split(', ')
    ner_list = recipe.get('NER', '').strip('[]').replace('"', '').split(', ')
    
    combined_list = []
    for ing, ner in zip(ingredients, ner_list):
        combined_list.append({
            'ingredient_text': ing,
            'name': ner,
            'quantity': None,
            'unit': None
        })
        
    if recipe:
        current_year = datetime.now().year
        return render_template('recipe_details.html', recipe=recipe, allergens=allergens, current_year=current_year, combined_list=combined_list)
    else:
        flash('Recipe not found.', 'error')
        return redirect(url_for('index'))
    
@app.route('/save_recipe/<recipeTitle>', methods=['POST'])
def save_recipe(recipeTitle):
    data = request.json  # Retrieve the JSON data sent from the frontend
    selected_products = data.get('selectedProducts', {})

    # Print the received data to the terminal (for debugging purposes)
    print(f"Saving recipe '{recipeTitle}' with selected products:")
    for ingredient, product in selected_products.items():
        print(f"Ingredient: {ingredient}, Product: {product}")

    # Further processing (e.g., saving to a database) can be done here
    session['selected_products'] = selected_products

    return jsonify({"success": True})


@app.route('/fetch_products')
def fetch_products():
    ingredient = request.args.get('ingredient')
    source = request.args.get('source', 'openfoodfacts')

    if source == 'openfoodfacts':
        products = fetch_ingredient_data(ingredient, limit=6)
    elif source == 'localdb':
        products = fetch_from_localdb(ingredient, limit=6)
    else:
        products = []

    return render_template('product_list.html', products=products)

# Route to handle allergen checking
@app.route('/check_allergens', methods=['POST'])
def check_allergens_route():
    data = request.get_json()
    selected_products = data.get('selectedProducts', {})
    selected_allergens = session.get('allergens', [])

    print("Selected Products Received:", selected_products)  # Debugging statement
    print("Selected Allergens from Session:", selected_allergens)  # Debugging statement

    # Run the allergen checker module
    allergens_found = check_allergens(selected_products, selected_allergens)

    return jsonify({'allergens_found': allergens_found})

# Route to handle nutrition calculation
@app.route('/calculate_nutrition', methods=['POST'])
def calculate_nutrition_route():
    data = request.get_json()
    selected_products = data.get('selectedProducts', {})

    print("Selected Products:", selected_products)  # Debugging statement

    total_nutrients = calculate_nutrition(selected_products)

    # Convert total_nutrients to a serializable format
    total_nutrients_serializable = {
        nutrient: {
            'amount': round(info['amount'], 2),
            'unit': info['unit']
        } for nutrient, info in total_nutrients.items()
    }

    print("Total Nutrients Serializable:", total_nutrients_serializable)  # Debugging statement

    return jsonify({'nutrition_info': total_nutrients_serializable})


    # Route to handle environmental impact calculation
    @app.route('/calculate_environmental_impact', methods=['POST'])
    def calculate_environmental_impact_route():
        selected_products = session.get('selected_products', {})

        # Run the environmental impact module
        environmental_impact = calculate_environmental_impact(selected_products)

        return jsonify({'environmental_impact': environmental_impact})


if __name__ == '__main__':
    app.run(debug=True)
