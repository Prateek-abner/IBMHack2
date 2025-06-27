document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const generateBtn = document.getElementById('generateBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsSection = document.getElementById('resultsSection');
    const errorSection = document.getElementById('errorSection');
    const testOutput = document.getElementById('testOutput');
    const apiInfo = document.getElementById('apiInfo');
    const downloadBtn = document.getElementById('downloadBtn');
    
    let currentFilename = '';
    
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('fileInput');
        const file = fileInput.files[0];
        
        if (!file) {
            showError('Please select a file');
            return;
        }
        
        generateBtn.disabled = true;
        loadingSpinner.classList.remove('d-none');
        hideResults();
        hideError();
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                showResults(data);
            } else {
                showError(data.error || 'Failed to generate test cases');
            }
        } catch (error) {
            showError('Network error: ' + error.message);
        } finally {
            generateBtn.disabled = false;
            loadingSpinner.classList.add('d-none');
        }
    });
    
    downloadBtn.addEventListener('click', function() {
        if (currentFilename) {
            window.location.href = `/download/${currentFilename}`;
        }
    });
    
    function showResults(data) {
        currentFilename = data.filename;
        
        apiInfo.innerHTML = `
            <strong>API:</strong> ${data.api_title}<br>
            <strong>Endpoints:</strong> ${data.endpoints_count}<br>
            <strong>Generated File:</strong> ${data.filename}
        `;
        
        testOutput.textContent = data.test_cases;
        resultsSection.classList.remove('d-none');
    }
    
    function showError(message) {
        document.getElementById('errorMessage').textContent = message;
        errorSection.classList.remove('d-none');
    }
    
    function hideResults() {
        resultsSection.classList.add('d-none');
    }
    
    function hideError() {
        errorSection.classList.add('d-none');
    }
});
