document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const resultsDiv = document.getElementById('results');
    const loadingBar = document.createElement('div');
    loadingBar.id = 'loading-bar';
    loadingBar.style.width = '0%';
    loadingBar.style.height = '5px';
    loadingBar.style.backgroundColor = '#4CAF50';
    loadingBar.style.transition = 'width 0.5s';

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        resultsDiv.innerHTML = '';
        resultsDiv.appendChild(loadingBar);

        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || `HTTP error! status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            loadingBar.style.width = '100%';
            if (!data || !data.results || data.results.length === 0) {
                throw new Error('Empty or invalid JSON response');
            }
            data.results.forEach(result => {
                const resultItem = document.createElement('div');
                resultItem.classList.add('result-item');
                resultItem.innerHTML = `
                    <span class="${result.passed ? 'success' : 'failure'}">
                        ${result.passed ? '✅' : '❌'}
                    </span>
                    <strong>${result.check}:</strong> ${result.message}
                `;
                resultsDiv.appendChild(resultItem);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            resultsDiv.innerHTML = `
                <div class="error-message">
                    <h3>An error occurred:</h3>
                    <p>${error.message}</p>
                </div>
            `;
            
            if (error.message === 'Google Slides Error') {
                const instructionsButton = document.createElement('button');
                instructionsButton.textContent = 'Show Instructions';
                instructionsButton.onclick = function() {
                    const instructionsDiv = document.getElementById('google-slides-instructions');
                    if (instructionsDiv.style.display === 'none') {
                        instructionsDiv.style.display = 'block';
                        instructionsButton.textContent = 'Hide Instructions';
                    } else {
                        instructionsDiv.style.display = 'none';
                        instructionsButton.textContent = 'Show Instructions';
                    }
                };
                resultsDiv.appendChild(instructionsButton);

                const instructionsDiv = document.createElement('div');
                instructionsDiv.id = 'google-slides-instructions';
                instructionsDiv.style.display = 'none';
                instructionsDiv.innerHTML = `
                    <h4>Instructions to set up Google Slides API credentials:</h4>
                    <ol>
                        <li>Go to the <a href="https://console.cloud.google.com/" target="_blank">Google Cloud Console</a></li>
                        <li>Create a new project or select an existing one</li>
                        <li>Enable the Google Slides API for your project</li>
                        <li>Create credentials (OAuth 2.0 Client ID) for a Desktop application</li>
                        <li>Download the credentials JSON file</li>
                        <li>Rename the file to 'google_credentials.json' and place it in a secure location</li>
                        <li>Set the GOOGLE_CREDENTIALS_PATH environment variable to the full path of the file</li>
                    </ol>
                `;
                resultsDiv.appendChild(instructionsDiv);
            }
        })
        .finally(() => {
            loadingBar.remove();
        });
    });
});
