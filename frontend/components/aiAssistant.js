const API_URL = 'http://localhost:8000/api/v1';

export function askAI(projectId, query) {
    return fetch(`${API_URL}/projects/${projectId}/ai_assistant`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
    })
    .then(response => response.json())
    .then(data => data.response)
    .catch(error => console.error('Error asking AI:', error));
}