async function submitMeal() {
    const meal_type = document.getElementById('meal_type').value;
    const content = document.getElementById('content').value;
    const calories = document.getElementById('calories').value;

    if (!content) {
        alert('Please describe your meal');
        return;
    }

    const response = await fetch('/api/log_meal', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ meal_type, content, calories })
    });

    if (response.ok) {
        location.reload();
    } else {
        alert('Error logging meal');
    }
}
