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
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (!data || (Array.isArray(data) && data.length === 0)) {
                throw new Error('Empty or invalid JSON response');
            }
            resultsDiv.innerHTML = '';
            if (data.error) {
                throw new Error(data.error);
            }
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
            return error.response ? error.response.text() : 'Unknown error occurred';
        })
        .then(errorText => {
            try {
                const errorJson = JSON.parse(errorText);
                resultsDiv.innerHTML = `<p>An error occurred: ${errorJson.error}</p>`;
            } catch (e) {
                console.error('Error parsing JSON:', e);
                resultsDiv.innerHTML = `<p>An error occurred: ${errorText}</p>`;
            }
        });
    });
});
