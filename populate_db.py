import sqlite3
import json

# Step 1: Create the SQLite database and table
def create_database():
    conn = sqlite3.connect('food_database.db')
    cursor = conn.cursor()
    
    # Create a table to store food information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY,
            description TEXT
        )
    ''')
    
    # Create a table to store nutrient information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nutrients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_id INTEGER,
            nutrient_name TEXT,
            amount REAL,
            unit TEXT,
            FOREIGN KEY(food_id) REFERENCES foods(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Step 2: Populate the database from JSON file
def populate_database(json_file_path):
    conn = sqlite3.connect('food_database.db')
    cursor = conn.cursor()
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for food in data['FoundationFoods']:
        # Insert food description into the foods table
        cursor.execute('INSERT INTO foods (description) VALUES (?)', (food['description'],))
        food_id = cursor.lastrowid
        
        # Insert nutrient information into the nutrients table
        for nutrient in food['foodNutrients']:
            nutrient_name = nutrient['nutrient']['name']
            amount = nutrient.get('amount', 0)
            unit = nutrient['nutrient']['unitName']
            cursor.execute('''
                INSERT INTO nutrients (food_id, nutrient_name, amount, unit)
                VALUES (?, ?, ?, ?)
            ''', (food_id, nutrient_name, amount, unit))
    
    conn.commit()
    conn.close()

# Step 3: Query the database for a specific ingredient
def fetch_nutritional_info(search_term, limit=5):
    conn = sqlite3.connect('food_database.db')
    cursor = conn.cursor()
    
    # Search for foods matching the search term
    cursor.execute('''
        SELECT id, description FROM foods
        WHERE description LIKE ?
        LIMIT ?
    ''', (f'%{search_term}%', limit))
    
    foods = cursor.fetchall()
    
    results = []
    for food_id, description in foods:
        # Get nutrient information for each food
        cursor.execute('''
            SELECT nutrient_name, amount, unit
            FROM nutrients
            WHERE food_id = ?
        ''', (food_id,))
        nutrients = cursor.fetchall()
        
        results.append({
            'name': description,
            'nutrients': [{'name': n[0], 'amount': n[1], 'unit': n[2]} for n in nutrients]
        })
    
    conn.close()
    return results

# Step 4: Main script
if __name__ == '__main__':
    create_database()
    populate_database('static/foundationDownload.json')  # Use the path to your JSON file
    
    # Example usage
    search_term = 'Hummus'
    result = fetch_nutritional_info(search_term)
    for food in result:
        print(f"Food: {food['name']}")
        for nutrient in food['nutrients']:
            print(f"  {nutrient['name']}: {nutrient['amount']} {nutrient['unit']}")
