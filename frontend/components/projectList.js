import { app } from '../app.js';
import { loadProjectDetails } from './projectDetails.js';

const API_URL = 'http://localhost:8000/api/v1';

export function loadProjects() {
    fetch(`${API_URL}/projects`)
        .then(response => response.json())
        .then(projects => {
            app.innerHTML = `
                <h2>My Projects</h2>
                <ul class="project-list">
                    ${projects.map(project => `
                        <li>
                            <h3>${project.name}</h3>
                            <p>${project.description}</p>
                            <button onclick="loadProjectDetails(${project.id})">View Details</button>
                        </li>
                    `).join('')}
                </ul>
            `;
        })
        .catch(error => console.error('Error loading projects:', error));
}

export function createProject(projectData) {
    return fetch(`${API_URL}/projects`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(projectData),
    })
    .then(response => response.json())
    .catch(error => console.error('Error creating project:', error));
}

// Make loadProjectDetails global so it can be called from inline onclick handlers
window.loadProjectDetails = loadProjectDetails;