import pint

# Initialize pint's UnitRegistry
ureg = pint.UnitRegistry()

def convert_to_grams(quantity, unit):
    """
    Converts the given quantity and unit into grams (or milliliters, if applicable).
    Handles errors gracefully if unit is undefined or conversion is not possible.
    """
    # Print the quantity and unit for debugging
    print(f"Debug: Quantity = {quantity}\n, Unit = {unit}")
    
    try:
        # Ensure quantity is a string or number for conversion
        if isinstance(quantity, list):  # Handle case if quantity is a list
            quantity = quantity[0]  # Use the first value of the list
            print(f"Debug: Quantity (after list check) = {quantity}")

        # Create a Quantity object using pint
        ingredient_quantity = ureg.Quantity(float(quantity), unit)
        
        # Convert to grams or milliliters based on unit type
        if unit in ['g', 'gram', 'grams']:
            return ingredient_quantity.magnitude
        else:
            return ingredient_quantity.to('grams').magnitude  # Default conversion to grams
    except pint.errors.DimensionalityError:
        print(f"Could not convert {quantity} {unit} to grams.")
        return None
    except pint.errors.UndefinedUnitError:
        print(f"Unit '{unit}' is not recognized in the unit registry. Skipping.")
        return None
    except ValueError:
        print(f"Invalid quantity '{quantity}' for unit '{unit}'. Skipping.")
        return None

