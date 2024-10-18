import sqlite3

def fetch_from_localdb(ingredient, limit=6):
    conn = sqlite3.connect('food_database.db')
    cursor = conn.cursor()

    # Search for foods matching the ingredient
    cursor.execute('''
        SELECT id, description FROM foods
        WHERE description LIKE ?
        LIMIT ?
    ''', (f'%{ingredient}%', limit))

    foods = cursor.fetchall()

    products = []
    for food_id, description in foods:
        # Get nutrient information for each food
        cursor.execute('''
            SELECT nutrient_name, amount, unit
            FROM nutrients
            WHERE food_id = ?
        ''', (food_id,))
        nutrients = cursor.fetchall()

        # Construct a product dictionary similar to Open Food Facts data
        product = {
            'product_name': description,
            'image_url': 'https://via.placeholder.com/150',  # Placeholder image
            'nutrients': [{'name': n[0], 'amount': n[1], 'unit': n[2]} for n in nutrients],
            # 'brands' and 'code' can be set to None or omitted
        }

        products.append(product)

    conn.close()
    return products
