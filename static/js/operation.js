
document.getElementById('action').addEventListener('change', function() {
    const action = this.value;
    const inputsDiv = document.getElementById('inputs');
    inputsDiv.innerHTML = ''; // Clear previous inputs

    if (action === 'eFermeture') {
        const etatsInput = document.createElement('input');
        etatsInput.setAttribute('type', 'text');
        etatsInput.setAttribute('name', 'etats');
        etatsInput.setAttribute('placeholder', 'États (séparés par des virgules)');
        inputsDiv.appendChild(etatsInput);
    } else if (action === 'decompose') {
        const motInput = document.createElement('input');
        motInput.setAttribute('type', 'text');
        motInput.setAttribute('name', 'mot');
        motInput.setAttribute('placeholder', 'Mot');
        inputsDiv.appendChild(motInput);
    } else if (action === 'reconnaitre') {
        const motsContainer = document.createElement('div');
        motsContainer.setAttribute('id', 'motsContainer');
        inputsDiv.appendChild(motsContainer);

        const addInputButton = document.getElementById('addInput');
        addInputButton.style.display = 'block'; // Show the add button

        addInputButton.addEventListener('click', function() {
            const inputContainer = document.createElement('div');

            const input = document.createElement('input');
            input.setAttribute('type', 'text');
            input.setAttribute('name', 'mots[]');
            input.setAttribute('placeholder', 'Mot');
            inputContainer.appendChild(input);

            const deleteButton = document.createElement('button');
            deleteButton.setAttribute('type', 'button');
            deleteButton.innerText = 'Supprimer';
            deleteButton.addEventListener('click', function() {
                motsContainer.removeChild(inputContainer);
            });
            inputContainer.appendChild(deleteButton);

            motsContainer.appendChild(inputContainer);
        });

        addInputButton.click();
    } else {
        document.getElementById('addInput').style.display = 'none'; // Hide the add button for other actions
    }
});
