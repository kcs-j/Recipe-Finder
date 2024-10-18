// Declare selectedProducts at the top of your script
let selectedProducts = {};

// Function to store selected products
function storeSelectedProduct(ingredientName, productData) {
    selectedProducts[ingredientName] = productData || 'None';
    console.log('Selected Products:', selectedProducts);
}

// Function to remove selected product
function removeSelectedProduct(ingredientName) {
    delete selectedProducts[ingredientName];
}

// Function to create the selected product card
function createSelectedProductCard(product) {
    const cardDiv = document.createElement('div');
    cardDiv.className = 'card h-100 product-card';
    cardDiv.innerHTML = `
        <img src="${product.image_url || '/static/images/placeholder.png'}" class="card-img-top" alt="${product.product_name || 'Product Image'}">
        <div class="card-body d-flex flex-column">
            <h5 class="card-title">${product.product_name || 'Unknown Product'}</h5>
            ${product.brands ? `<p class="card-text"><strong>Brand:</strong> ${product.brands}</p>` : ''}
            ${product.nutrients ? `
                <h6>Nutritional Information:</h6>
                <ul class="list-unstyled">
                    ${product.nutrients
                        .filter(nutrient => ['Energy', 'Total lipid (fat)', 'Cholesterol', 'Protein', 'Sodium, Na'].includes(nutrient.name))
                        .map(nutrient => `<li>${nutrient.name}: ${nutrient.amount} ${nutrient.unit}</li>`)
                        .join('')}
                </ul>` : ''
            }
            <div class="mt-auto">
                ${product.code ? `<a href="https://world.openfoodfacts.org/product/${product.code}" target="_blank" class="btn btn-secondary btn-sm w-100 mb-2">View on OpenFoodFacts</a>` : ''}
                <button class="btn btn-warning btn-sm w-100 change-product">Change Product</button>
            </div>
        </div>
    `;

    // Attach listener to "Change Product" button
    cardDiv.querySelector('.change-product').addEventListener('click', (event) => {
        const productContainer = event.target.closest('.product-container');
        const ingredientHeader = productContainer.previousElementSibling;
        // Enable the search inputs
        ingredientHeader.querySelectorAll('input, select, button').forEach(elem => {
            elem.disabled = false;
        });
        // Clear stored selected product
        const ingredientName = ingredientHeader.querySelector('input').value;
        removeSelectedProduct(ingredientName);
        // Clear the product container
        productContainer.innerHTML = '';
        productContainer.style.display = 'none';
    });
    return cardDiv;
}

// Function to handle product selection
function attachProductSelectionListeners() {
    const selectButtons = document.querySelectorAll('.select-product');
    selectButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            const button = event.target;
            const productData = JSON.parse(button.getAttribute('data-product'));
            const productCard = button.closest('.product-card');
            const productContainer = productCard.closest('.product-container');
            const ingredientProductDiv = productContainer.closest('.ingredient-product');
            const ingredientHeader = ingredientProductDiv.querySelector('.ingredient-header');
            const ingredientName = ingredientHeader.querySelector('input').value;

            console.log('Ingredient Name:', ingredientName); // Debugging statement

            // Store the selected product
            storeSelectedProduct(ingredientName, productData);

            // Update the UI
            // Hide other products
            productContainer.innerHTML = '';
            productContainer.style.display = 'block';

            // Display the selected product prominently
            productContainer.appendChild(createSelectedProductCard(productData));

            // Optionally, disable the search inputs
            ingredientHeader.querySelectorAll('input, select, button').forEach(elem => {
                elem.disabled = true;
            });
        });
    });
}

// Update fetchProducts function to attach selection listeners after loading products
function fetchProducts(ingredient, containerId, source) {
    const container = document.getElementById(containerId);
    container.innerHTML = '<p>Loading products...</p>';
    container.style.display = 'block';

    fetch(`/fetch_products?ingredient=${encodeURIComponent(ingredient)}&source=${encodeURIComponent(source)}`)
        .then(response => response.text())
        .then(html => {
            container.innerHTML = html;
            // Attach listeners to new select buttons
            attachProductSelectionListeners();
        })
        .catch(error => {
            console.error('Error fetching products:', error);
            container.innerHTML = '<p>Error fetching products.</p>';
        });
}

// Functions to display results
function displayAllergenResults(data) {
    const container = document.getElementById('allergen-results');
    container.innerHTML = '';  // Clear previous results

    if (data.allergens_found && data.allergens_found.length > 0) {
        container.innerHTML = `
            <div class="alert alert-danger">
                The following allergens were found in your selected products: ${data.allergens_found.join(', ')}
            </div>
        `;
    } else {
        container.innerHTML = `
            <div class="alert alert-success">
                No allergens found in your selected products.
            </div>
        `;
    }
}

function displayNutritionResults(data) {
    const container = document.getElementById('nutrition-results');
    container.innerHTML = '';  // Clear previous results

    if (data.nutrition_info) {
        let nutritionHtml = '<h3>Nutritional Information</h3><ul>';
        for (const [nutrient, value] of Object.entries(data.nutrition_info)) {
            nutritionHtml += `<li>${nutrient}: ${value}</li>`;
        }
        nutritionHtml += '</ul>';
        container.innerHTML = nutritionHtml;
    } else {
        container.innerHTML = `
            <div class="alert alert-warning">
                Unable to calculate nutritional information.
            </div>
        `;
    }
}

function displayEnvironmentalResults(data) {
    const container = document.getElementById('environmental-results');
    container.innerHTML = '';  // Clear previous results

    if (data.environmental_impact) {
        let environmentalHtml = '<h3>Environmental Impact</h3><ul>';
        for (const [impact, value] of Object.entries(data.environmental_impact)) {
            environmentalHtml += `<li>${impact}: ${value}</li>`;
        }
        environmentalHtml += '</ul>';
        container.innerHTML = environmentalHtml;
    } else {
        container.innerHTML = `
            <div class="alert alert-warning">
                Unable to calculate environmental impact.
            </div>
        `;
    }
}

// Function to show visual feedback to the user
function showFeedback(message, type) {
    const feedbackContainer = document.createElement('div');
    feedbackContainer.className = `alert alert-${type} mt-3`;  // Bootstrap alert classes for styling
    feedbackContainer.textContent = message;

    // Append the feedback message to the DOM
    document.body.appendChild(feedbackContainer);

    // Remove the feedback message after 3 seconds
    setTimeout(() => {
        feedbackContainer.remove();
    }, 3000);
}

document.addEventListener('DOMContentLoaded', () => {
    // Allergen handling code
    const selectedAllergensContainer = document.getElementById('selected-allergens');
    const availableAllergensContainer = document.getElementById('available-allergens');
    const allergenInput = document.getElementById('allergen');
    const allergensHiddenInput = document.getElementById('allergens-hidden');
    const form = document.getElementById('allergen-form');

    // Check if elements exist before proceeding
    if (selectedAllergensContainer && availableAllergensContainer && allergenInput && allergensHiddenInput && form) {
        // Load allergens from a text file and populate the list
        fetch('/static/allergens.txt')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.text();
            })
            .then(data => {
                const allergens = data.split('\n').filter(allergen => allergen.trim() !== '');
                allergens.forEach(allergen => {
                    createTag(allergen, availableAllergensContainer, false);
                });
            })
            .catch(error => {
                console.error('Error fetching allergens:', error);
            });

        // Handle allergen input
        allergenInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const allergen = allergenInput.value.trim();
                if (allergen !== '') {
                    createTag(allergen, selectedAllergensContainer, true);
                    allergenInput.value = '';
                }
            }
        });

        // Update the hidden input when the form is submitted
        form.addEventListener('submit', () => {
            const selectedAllergens = Array.from(selectedAllergensContainer.children).map(tag => tag.textContent.replace('×', '').trim());
            allergensHiddenInput.value = selectedAllergens.join(',');
        });

        function createTag(allergen, container, isSelected) {
            if (!container) {
                console.error('Container not found for allergen:', allergen);
                return;
            }
            const tag = document.createElement('div');
            tag.classList.add('tag');
            tag.textContent = allergen;

            const removeIcon = document.createElement('span');
            removeIcon.classList.add('remove');
            removeIcon.textContent = '×';
            removeIcon.addEventListener('click', () => {
                container.removeChild(tag);
                if (isSelected) {
                    createTag(allergen, availableAllergensContainer, false);
                }
            });
            tag.appendChild(removeIcon);

            if (!isSelected) {
                tag.addEventListener('click', () => {
                    container.removeChild(tag);
                    createTag(allergen, selectedAllergensContainer, true);
                });
            }

            container.appendChild(tag);
        }
    } else {
        console.warn('Allergen elements not found in the DOM.');
    }

    // Allergen List (Removal)
    const recipeNameHiddenElement = document.getElementById('recipe-name-hidden');
    const recipeTitleHiddenElement = document.getElementById('recipe-title-hidden');

    function attachRemoveListeners() {
        const removeButtons = document.querySelectorAll('.remove');
        removeButtons.forEach(button => {
            button.addEventListener('click', (event) => {
                const allergen = event.target.getAttribute('data-allergen');

                // Remove the allergen tag from the DOM
                event.target.parentElement.remove();

                // Collect the updated list of allergens
                const updatedAllergens = Array.from(document.querySelectorAll('#selected-allergens .tag'))
                    .map(tag => tag.textContent.replace('×', '').trim());


                // Determine the URL and body based on the page
                let fetchUrl = '';
                let fetchBody = '';

                if (recipeNameHiddenElement) {
                    // On results.html
                    const recipeNameHidden = recipeNameHiddenElement.value;
                    fetchUrl = '/search';
                    fetchBody = `allergens=${encodeURIComponent(updatedAllergens.join(','))}&recipe=${encodeURIComponent(recipeNameHidden)}`;
                } else if (recipeTitleHiddenElement) {
                    // On recipe_details.html
                    const recipeTitle = recipeTitleHiddenElement.value;
                    fetchUrl = `/recipe_details/${encodeURIComponent(recipeTitle)}`;
                    fetchBody = `allergens=${encodeURIComponent(updatedAllergens.join(','))}`;
                }

                // Send a POST request with the updated allergens list
                fetch(fetchUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: fetchBody
                })
                .then(response => response.text())
                .then(html => {
                    // Parse the response and update only the relevant parts of the page
                    const parser = new DOMParser();
                    const newDocument = parser.parseFromString(html, 'text/html');
                    document.getElementById('allergens-section').innerHTML = newDocument.getElementById('allergens-section').innerHTML;

                    // Update other sections if necessary
                    if (document.getElementById('recipes-section') && newDocument.getElementById('recipes-section')) {
                        // On results.html
                        document.getElementById('recipes-section').innerHTML = newDocument.getElementById('recipes-section').innerHTML;
                    }

                    // Reattach the listeners to the newly added elements
                    attachRemoveListeners();
                })
                .catch(error => {
                    console.error('Error updating page:', error);
                });
            });
        });
    }

    // Initial binding of remove listeners
    attachRemoveListeners();

    // Event listener for the Save Recipe button
    const saveRecipeButton = document.getElementById('save-recipe');
    if (saveRecipeButton) {
        saveRecipeButton.addEventListener('click', () => {
            console.log('Save Recipe button clicked.');
            const recipeTitleHiddenElement = document.getElementById('recipe-title-hidden');
            const recipeTitle = recipeTitleHiddenElement ? recipeTitleHiddenElement.value : '';

            // Send selected products to the server
            fetch(`/save_recipe/${encodeURIComponent(recipeTitle)}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ selectedProducts }),  // Send the selected products to the backend
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showFeedback('Recipe saved successfully!', 'success');
                } else {
                    showFeedback('Error saving recipe. Please try again.', 'danger');
                }
            })
            .catch(error => {
                console.error('Error saving recipe:', error);
                showFeedback('Error saving recipe. Please try again.', 'danger');
            });
        });
    } else {
        console.error('Save Recipe Button not found.');
    }

    // Event listener for the Check Allergens button
    const checkAllergensButton = document.getElementById('check-allergens');
    if (checkAllergensButton) {
        checkAllergensButton.addEventListener('click', () => {
            console.log('Check Allergens button clicked.');
            console.log('Selected Products:', selectedProducts);

            // Send selected products to the server
            fetch('/check_allergens', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ selectedProducts }),  // Send the selected products to the backend
            })
            .then(response => response.json())
            .then(data => {
                displayAllergenResults(data);
            })
            .catch(error => {
                console.error('Error checking allergens:', error);
            });
        });
    } else {
        console.error('Check Allergens Button not found.');
    }

    // Event listener for the Calculate Nutrition button
    const calculateNutritionButton = document.getElementById('calculate-nutrition');
    if (calculateNutritionButton) {
        calculateNutritionButton.addEventListener('click', () => {
            // Send selected products to the server
            fetch('/calculate_nutrition', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ selectedProducts }),
            })
            .then(response => response.json())
            .then(data => {
                displayNutritionResults(data);
            })
            .catch(error => {
                console.error('Error calculating nutrition:', error);
            });
        });
    } else {
        console.error('Calculate Nutrition Button not found.');
    }

    // Event listener for the Environmental Impact button
    const environmentalImpactButton = document.getElementById('calculate-environmental-impact');
    if (environmentalImpactButton) {
        environmentalImpactButton.addEventListener('click', () => {
            // Send selected products to the server
            fetch('/calculate_environmental_impact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ selectedProducts }),
            })
            .then(response => response.json())
            .then(data => {
                displayEnvironmentalResults(data);
            })
            .catch(error => {
                console.error('Error calculating environmental impact:', error);
            });
        });
    } else {
        console.error('Environmental Impact Button not found.');
    }

    // Attach product selection listeners after the DOM is loaded
    attachProductSelectionListeners();
});

// Additional functions that don't need to be inside DOMContentLoaded
function openTextEditor() {
    const modal = new bootstrap.Modal(document.getElementById('customRecipeModal'));
    modal.show();
}

function saveCustomRecipe() {
    const recipeText = document.getElementById('custom-recipe-text').value;

    // Collect the selected allergens
    const selectedAllergens = Array.from(document.querySelectorAll('#selected-allergens .tag'))
        .map(tag => tag.textContent.replace('×', '').trim());

    // Send the recipe input and allergens to the Flask server
    fetch('/custom_recipe', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            recipe: recipeText,
            allergens: selectedAllergens
        }),
    })
    .then(response => {
        // Check if the response is OK
        if (response.ok) {
            return response.text(); // Get the HTML content from the server
        } else {
            throw new Error('Failed to save recipe');
        }
    })
    .then(data => {
        // Replace the current page content with the new HTML
        document.open();
        document.write(data);
        document.close();
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}


function toggleProducts(containerId) {
    const container = document.getElementById(containerId);
    if (container.style.display === 'none' || container.style.display === '') {
        container.style.display = 'block';
    } else {
        container.style.display = 'none';
    }
}
