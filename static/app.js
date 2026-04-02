document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('itinerary-form');
    const resultsContainer = document.getElementById('results-container');
    const loadingIndicator = document.getElementById('loading-indicator');
    const itineraryOutput = document.getElementById('itinerary-output');
    
    const destTitle = document.getElementById('destination-title');
    const ratingStat = document.getElementById('rating-stat');
    const matchStat = document.getElementById('match-stat');
    const financeBox = document.getElementById('finance-box');
    const itineraryBox = document.getElementById('itinerary-box');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Grab inputs
        const city = document.getElementById('city').value;
        const attributesRaw = document.getElementById('attributes').value;
        const days = parseInt(document.getElementById('days').value);
        
        // Clean attributes into array
        const attributes = attributesRaw.split(',').map(item => item.trim()).filter(item => item);
        
        // UI State: Loading
        resultsContainer.classList.remove('hidden');
        loadingIndicator.classList.remove('hidden');
        itineraryOutput.classList.add('hidden');
        
        try {
            // Hit FastAPI Route
            const response = await fetch('/api/generate_itinerary', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    city: city,
                    attributes: attributes,
                    days: days
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Failed to fetch itinerary');
            }
            
            // Populate View Components
            const dest = data.destination;
            destTitle.innerText = `🌟 ${dest.Place}, ${dest.City}`;
            ratingStat.innerText = `⭐ Rating: ${dest.Rating}/5`;
            matchStat.innerText = `🎯 Match: ${dest.MatchScore}%`;
            
            // Render markdown (if marked.js is loaded)
            financeBox.innerHTML = typeof marked !== 'undefined' 
                ? marked.parse(data.financial_estimate) 
                : `<pre>${data.financial_estimate}</pre>`;
                
            itineraryBox.innerHTML = typeof marked !== 'undefined' 
                ? marked.parse(data.itinerary) 
                : `<pre>${data.itinerary}</pre>`;
                
            // UI State: Complete
            loadingIndicator.classList.add('hidden');
            itineraryOutput.classList.remove('hidden');
            
        } catch (error) {
            alert(`Error: ${error.message}`);
            loadingIndicator.classList.add('hidden');
        }
    });
});
