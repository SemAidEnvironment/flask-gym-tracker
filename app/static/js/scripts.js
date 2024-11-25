document.getElementById('add-exercise-btn').addEventListener('click', function () {
    const container = document.getElementById('exercise-container');
    const count = container.children.length + 1;

    const newExercise = document.createElement('div');
    newExercise.classList.add('exercise');
    newExercise.innerHTML = `
        <h3>Exercise ${count}</h3>
        <label>Choose an Exercise:
            <select name="exercise_name" required onchange="fetchLastExercise(this)">
                <option value="" disabled selected>Select an exercise</option>
                ${exercises.map(ex => `<option value="${ex}">${ex}</option>`).join('')}
            </select>
        </label>
        <label>Sets: <input type="number" name="sets" required></label>
        <label>Repetitions: <input type="number" name="reps" required></label>
        <label>Weight (kg): <input type="number" step="0.1" name="weight" required></label>
        <button type="button" class="remove-btn" onclick="removeExercise(this)">Remove</button>
    `;
    container.appendChild(newExercise);
});

function removeExercise(button) {
    const exerciseDiv = button.closest('.exercise');
    exerciseDiv.remove();
}
