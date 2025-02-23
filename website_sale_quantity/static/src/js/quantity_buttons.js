/**
 * Increment and Decrement Quantity Buttons
 */
function incrementQuantity(button) {
    var input = button.closest('.quantity-input-group').querySelector('input[name="add_qty"]');
    input.value = parseInt(input.value) + 1;
}

function decrementQuantity(button) {
    var input = button.closest('.quantity-input-group').querySelector('input[name="add_qty"]');
    if (input.value > 1) {
        input.value = parseInt(input.value) - 1;
    }
}