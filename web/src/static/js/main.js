
document.addEventListener('DOMContentLoaded', () => {
    const dropdown = document.getElementById('symptom-dropdown');
    const searchInput = document.getElementById('symptom-search');
    const selectedList = document.getElementById('selected-list');
    const symptomsList = document.getElementById('symptoms-list');
    const symptomItems = symptomsList.querySelectorAll('li');
    const predictBtn = document.getElementById('predict-btn');
    const modelSelect = document.getElementById('model-select');
    const resultContainer = document.getElementById('result-container');
    
    let selectedSymptoms = new Set();

    // Toggle dropdown
    selectedList.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove')) return;
        dropdown.classList.toggle('active');
        if (dropdown.classList.contains('active')) {
            searchInput.focus();
        }
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!dropdown.contains(e.target)) {
            dropdown.classList.remove('active');
        }
    });

    // Search filter
    searchInput.addEventListener('input', () => {
        const filter = searchInput.value.toLowerCase();
        symptomItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(filter) ? 'block' : 'none';
        });
    });

    // Select symptom
    symptomsList.addEventListener('click', (e) => {
        if (e.target.tagName === 'LI') {
            const val = e.target.getAttribute('data-value');
            toggleSymptom(val, e.target);
        }
    });

    function toggleSymptom(val, element) {
        if (selectedSymptoms.has(val)) {
            selectedSymptoms.delete(val);
            if (element) element.classList.remove('selected');
            removeTag(val);
        } else {
            selectedSymptoms.add(val);
            if (element) element.classList.add('selected');
            addTag(val);
        }
        updatePlaceholder();
    }

    function addTag(val) {
        const tag = document.createElement('span');
        tag.className = 'tag';
        tag.setAttribute('data-value', val);
        tag.innerHTML = `${val} <span class="remove">&times;</span>`;
        
        tag.querySelector('.remove').addEventListener('click', () => {
            toggleSymptom(val, [...symptomItems].find(i => i.getAttribute('data-value') === val));
        });
        
        selectedList.appendChild(tag);
    }

    function removeTag(val) {
        const tag = selectedList.querySelector(`.tag[data-value="${val}"]`);
        if (tag) tag.remove();
    }

    function updatePlaceholder() {
        const placeholder = selectedList.querySelector('.placeholder');
        if (selectedSymptoms.size > 0) {
            placeholder.style.display = 'none';
        } else {
            placeholder.style.display = 'block';
        }
    }

    // Prediction
    predictBtn.addEventListener('click', async () => {
        if (selectedSymptoms.size === 0) {
            alert('Please select at least one symptom.');
            return;
        }

        predictBtn.disabled = true;
        predictBtn.textContent = 'Analyzing...';
        
        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    symptoms: Array.from(selectedSymptoms),
                    model: modelSelect.value
                })
            });

            const result = await response.json();
            displayResult(result);
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while predicting.');
        } finally {
            predictBtn.disabled = false;
            predictBtn.textContent = 'Analyze Risk';
        }
    });

    function displayResult(result) {
        resultContainer.classList.remove('hidden');
        const riskBox = document.getElementById('risk-box');
        const riskLabel = document.getElementById('risk-label');
        const gaugeFill = document.getElementById('gauge-fill');
        const confidenceText = document.getElementById('confidence-text');

        riskLabel.textContent = result.prediction_label;
        
        if (result.prediction === 1) {
            riskBox.className = 'risk-indicator risk-dangerous';
        } else {
            riskBox.className = 'risk-indicator risk-normal';
        }

        // Update Gauge
        const confidence = result.confidence || 0.5;
        const percentage = Math.round(confidence * 100);
        confidenceText.textContent = `Confidence: ${percentage}%`;
        
        // Calculate rotation: 0% = 0deg, 100% = 180deg
        // Since it's a half-circle, we rotate the fill
        // Normal (0) usually left-side (green), Dangerous (1) right-side (red)
        let rotation = 0;
        if (result.prediction === 1) {
            // Highly dangerous -> 120 to 180 deg
            rotation = 90 + (confidence * 90);
        } else {
            // Highly normal -> 0 to 60 deg
            rotation = (1 - confidence) * 90;
        }
        
        gaugeFill.style.transform = `rotate(${rotation}deg)`;
        
        // Scroll to result
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }
});
