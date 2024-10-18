# environmental_impact.py

def calculate_environmental_impact(selected_products):
    environmental_totals = {}

    # Environmental data may be scarce; handle missing data gracefully
    for ingredient, product in selected_products.items():
        environmental_data = product.get('environmental_data', {})
        for impact, value in environmental_data.items():
            if impact not in environmental_totals:
                environmental_totals[impact] = 0
            environmental_totals[impact] += value

    return environmental_totals
