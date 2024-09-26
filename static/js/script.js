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
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const reader = response.body.getReader();
            return new ReadableStream({
                start(controller) {
                    return pump();
                    function pump() {
                        return reader.read().then(({ done, value }) => {
                            if (done) {
                                controller.close();
                                return;
                            }
                            controller.enqueue(value);
                            return pump();
                        });
                    }
                }
            });
        })
        .then(stream => new Response(stream))
        .then(response => response.json())
        .then(data => {
            loadingBar.style.width = '100%';
            if (!data || (Array.isArray(data) && data.length === 0)) {
                throw new Error('Empty or invalid JSON response');
            }
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
                    <strong>${result.check}:</strong> ${result.message}
                `;
                resultsDiv.appendChild(resultItem);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            resultsDiv.innerHTML = `<p class="error">An error occurred: ${error.message}</p>`;
        })
        .finally(() => {
            loadingBar.remove();
        });
    });
});
