document.addEventListener('DOMContentLoaded', () => {
    const transitionsContainer = document.getElementById('transitions');
    const addTransitionBtn = document.getElementById('add-transition-btn');

    transitionsContainer.addEventListener('click', (event) => {
        if (event.target.classList.contains('delete-btn')) {
            event.target.parentElement.remove();
        }
    });

    addTransitionBtn.addEventListener('click', () => {
        const newTransition = document.createElement('div');
        newTransition.classList.add('transition');
        newTransition.innerHTML = `
            (
            <input type="text" name="origine[]" placeholder="origine" required>, 
            <input type="text" name="lettre[]" placeholder="lettre" required>, 
            <input type="text" name="destinations[]" placeholder="destinations" required>
            )
            <button type="button" class="delete-btn">❌</button>
        `;
        transitionsContainer.appendChild(newTransition);
    });
});
