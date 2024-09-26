document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const resultsDiv = document.getElementById('results');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);

        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            resultsDiv.innerHTML = '';
            data.forEach(result => {
                const resultItem = document.createElement('div');
                resultItem.classList.add('result-item');
                resultItem.innerHTML = `
                    <span class="${result.passed ? 'success' : 'failure'}">
                        ${result.passed ? '✅' : '❌'}
                    </span>
                    ${result.check}: ${result.message}
                `;
                resultsDiv.appendChild(resultItem);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            resultsDiv.innerHTML = '<p>An error occurred while processing your request.</p>';
        });
    });
});
