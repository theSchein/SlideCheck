let currentPage = 1;
let currentFilter = 'all';

function filterSubmissions(filter) {
    currentFilter = filter;
    currentPage = 1;
    loadSubmissions();
}

function changePage(delta) {
    currentPage += delta;
    if (currentPage < 1) currentPage = 1;
    loadSubmissions();
}

function loadSubmissions() {
    fetch(`/api/submissions?page=${currentPage}&filter=${currentFilter}`)
        .then(response => response.json())
        .then(data => {
            updateSubmissionsTable(data.submissions);
            updatePagination(data.current_page, data.total_pages);
        });
}

function updateSubmissionsTable(submissions) {
    const tableBody = document.getElementById('submissions-table');
    tableBody.innerHTML = '';
    submissions.forEach(submission => {
        const row = document.createElement('tr');
        row.className = `submission-row ${submission.passed ? 'passed' : 'failed'}`;
        row.innerHTML = `
            <td>${submission.id}</td>
            <td>${submission.filename || `<a href="${submission.url}" target="_blank">${submission.url}</a>`}</td>
            <td>${submission.timestamp}</td>
            <td>
                <span class="status-indicator ${submission.passed ? 'passed' : 'failed'}">
                    ${submission.passed ? '✓' : '✗'}
                </span>
            </td>
            <td>
                <button onclick="viewDetails(${submission.id})">View Details</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

function updatePagination(currentPage, totalPages) {
    document.getElementById('current-page').textContent = currentPage;
    document.querySelector('button[onclick="changePage(-1)"]').disabled = currentPage === 1;
    document.querySelector('button[onclick="changePage(1)"]').disabled = currentPage === totalPages;
}

function viewDetails(submissionId) {
    fetch(`/api/submission/${submissionId}`)
        .then(response => response.json())
        .then(data => {
            const modal = document.getElementById('modal');
            const modalContent = document.getElementById('modal-content');
            modalContent.innerHTML = `
                <h3>${data.filename || data.url}</h3>
                <p>Timestamp: ${data.timestamp}</p>
                <p>Status: ${data.passed ? 'Passed' : 'Failed'}</p>
                <h4>Check Results:</h4>
                <ul>
                    ${data.results.map(result => `
                        <li>
                            <strong>${result.check}:</strong> 
                            <span class="${result.passed ? 'success' : 'failure'}">
                                ${result.passed ? 'Passed' : 'Failed'}
                            </span>
                            - ${result.message}
                        </li>
                    `).join('')}
                </ul>
            `;
            modal.style.display = 'block';
        });
}

function downloadMasterDeck() {
    window.location.href = '/download_master_deck';
}

// Close modal when clicking on the close button or outside the modal
window.onclick = function(event) {
    const modal = document.getElementById('modal');
    if (event.target == modal || event.target.className == 'close') {
        modal.style.display = 'none';
    }
}

// Initial load
loadSubmissions();
