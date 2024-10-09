import { app } from '../app.js';

const API_URL = 'http://localhost:8000/api/v1';

export function loadTasks(projectId) {
    fetch(`${API_URL}/projects/${projectId}/tasks`)
        .then(response => response.json())
        .then(tasks => {
            app.innerHTML = `
                <h3>Tasks</h3>
                <ul class="task-list">
                    ${tasks.map(task => `
                        <li>
                            <h4>${task.title}</h4>
                            <p>${task.description}</p>
                            <p>Status: ${task.status}</p>
                            <p>Priority: ${task.priority}</p>
                        </li>
                    `).join('')}
                </ul>
            `;
        })
        .catch(error => console.error('Error loading tasks:', error));
}

export function createTask(projectId, taskData) {
    return fetch(`${API_URL}/projects/${projectId}/tasks`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(taskData),
    })
    .then(response => response.json())
    .catch(error => console.error('Error creating task:', error));
}