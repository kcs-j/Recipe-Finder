import requests
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
import pandas as pd

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')
OFF_API_URL = "https://world.openfoodfacts.org/cgi/search.pl"

recipes_df = pd.read_csv('Recipedata.csv')
top_100_recipes = recipes_df[['title', 'link']].head(100)

@app.before_request
def initialize_saved_recipes():
    if 'saved_recipes' not in session:
        session['saved_recipes'] = []

@app.route('/')
def index():
    page = int(request.args.get('page', 1))
    per_page = 10

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    paginated_recipes = top_100_recipes.iloc[start_idx:end_idx]

    total_pages = len(top_100_recipes) // per_page

    return render_template('index.html',paginated_recipes=paginated_recipes.to_dict(orient='records'), page=page, total_pages=total_pages)

@app.route('/custom_recipe', methods=['POST'])
def custom_recipe():
    #Get the custom recipe text and allergens from the JSON data
    data = request.get_json()
    recipe_text = data.get('recipe', '')
    allergens = data.get('allergens', [])
    allergens = [allergen.strip() for allergen in allergens if allergen.strip()]  #Clean up allergens list

    #Store allergens in the session
    session['allergens'] = allergens

    #Split the recipe input by line and parse ingredients
    ingredient_lines = recipe_text.strip().split('\n')
    parsed_recipe, parsed_ingredients = parse_multiple_ingredients(ingredient_lines)

    #Create a combined list for consistency with existing template
    combined_list = []
    for ingredient in parsed_ingredients:
        combined_list.append({
            'ingredient_text': ingredient.ingredient_text,
            'name': ingredient.name,
            'quantity': ingredient.quantity,
            'unit': ingredient.unit,
        })

    #Render the recipe details page with the custom recipe and combined list
    return render_template('recipe_details.html', recipe=parsed_recipe, is_custom=True, allergens=allergens, combined_list=combined_list)

@app.route('/search', methods=['POST','GET'])
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

@app.route('/save_recipe/<recipe_title>')
def save_recipe(recipe_title):
    saved_recipes = session['saved_recipes']
    if recipe_title not in saved_recipes:
        saved_recipes.append(recipe_title)
        session['saved_recipes'] = saved_recipes  # 更新会话中的保存列表
    return redirect(url_for('saved_recipes'))

@app.route('/saved_recipes')
def saved_recipes():
    saved_recipes = session.get('saved_recipes', [])
    saved_recipe_details = recipes_df[recipes_df['title'].isin(saved_recipes)].to_dict(orient='records')
    # 获取用户选择的优先级选项
    priority = request.args.get('priority', 'none')
    return render_template('saved_recipes.html', recipes=saved_recipe_details, priority=priority)

@app.route('/unsave_recipe/<recipe_title>')
def unsave_recipe(recipe_title):
    if 'saved_recipes' in session:
        # 从会话中获取已保存的食谱列表
        saved_recipes = session['saved_recipes']
        # 如果食谱在列表中，则移除
        if recipe_title in saved_recipes:
            saved_recipes.remove(recipe_title)
            session['saved_recipes'] = saved_recipes
    return redirect(url_for('saved_recipes'))

@app.route('/ingredient_search/<ingredient>')
def ingredient_search(ingredient):
    priority = request.args.get('priority', 'none')
    nutri_score_filter = request.args.get('nutri_score_filter', 'all')
    eco_score_filter = request.args.get('eco_score_filter', 'all')
    params = {
        'search_terms': ingredient,
        'search_simple': '1',
        'action': 'process',
        'json': '1'
    }
    response = requests.get(OFF_API_URL, params=params)
    data = response.json()

    products = data.get('products', [])

    if nutri_score_filter != 'all':
        products = [product for product in products if
                    product.get('nutriscore_grade', '').upper() == nutri_score_filter]

    if eco_score_filter != 'all':
        products = [product for product in products if product.get('ecoscore_grade', '').upper() == eco_score_filter]
    # 根据用户选择的优先级排序
    if priority == 'nutriscore':
        products = sorted(products, key=lambda x: x.get('nutriscore_grade', 'z'))
    elif priority == 'ecoscore':
        products = sorted(products, key=lambda x: x.get('ecoscore_grade', 'z'))

    return render_template('ingredient_results.html', ingredient=ingredient, products=products)

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

@app.route('/select_product', methods=['POST'])
def select_product():
    recipe_title = request.form['recipe_title']
    ingredient = request.form['ingredient']
    product_name = request.form['product_name']
    nutriscore = request.form['nutriscore']
    ecoscore = request.form['ecoscore']

    selected_products = session.get('selected_products', {})

    if recipe_title not in selected_products:
        selected_products[recipe_title] = []

    selected_products[recipe_title] = [
        product for product in selected_products[recipe_title]
        if product['ingredient'] != ingredient
    ]

    selected_products[recipe_title].append({
        'ingredient': ingredient,
        'product_name': product_name,
        'nutriscore': nutriscore,
        'ecoscore': ecoscore
    })

    session['selected_products'] = selected_products
    return redirect(url_for('saved_recipes'))
@app.route('/remove_product', methods=['POST'])
def remove_product():
    recipe_title = request.form['recipe_title']
    ingredient = request.form['ingredient']
    product_name = request.form['product_name']
    selected_products = session.get('selected_products', {})

    if recipe_title in selected_products:
        selected_products[recipe_title] = [
            product for product in selected_products[recipe_title]
            if not (product['ingredient'] == ingredient and product['product_name'] == product_name)
        ]
        if not selected_products[recipe_title]:
            del selected_products[recipe_title]
        session['selected_products'] = selected_products
    return redirect(url_for('saved_recipes'))

@app.route('/return_to_results')
def return_to_results():
    last_search = session.get('last_search', [])
    last_allergen = session.get('last_allergen', '')
    if last_search:
        return render_template('results.html', recipes=last_search, allergen=last_allergen)
    return redirect(url_for('index'))


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


    #Route to handle environmental impact calculation
    @app.route('/calculate_environmental_impact', methods=['POST'])
    def calculate_environmental_impact_route():
        selected_products = session.get('selected_products', {})

        # Run the environmental impact module
        environmental_impact = calculate_environmental_impact(selected_products)

        return jsonify({'environmental_impact': environmental_impact})


if __name__ == '__main__':
    app.run(debug=True)
