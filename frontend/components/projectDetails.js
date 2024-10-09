import { app } from '../app.js';
import { loadTasks, createTask } from './taskList.js';
import { askAI } from './aiAssistant.js';

const API_URL = 'http://localhost:8000/api/v1';

export function loadProjectDetails(projectId) {
    fetch(`${API_URL}/projects/${projectId}`)
        .then(response => response.json())
        .then(project => {
            app.innerHTML = `
                <h2>${project.name}</h2>
                <p>${project.description}</p>
                <button onclick="loadTasks(${project.id})">View Tasks</button>
                <button onclick="showCreateTaskForm(${project.id})">Create Task</button>
                <button onclick="showAIAssistant(${project.id})">AI Assistant</button>
            `;
        })
        .catch(error => console.error('Error loading project details:', error));
}

function showCreateTaskForm(projectId) {
    app.innerHTML += `
        <h3>Create New Task</h3>
        <form id="createTaskForm">
            <input type="text" id="taskName" placeholder="Task Name" required>
            <textarea id="taskDescription" placeholder="Task Description" required></textarea>
            <button type="submit">Create Task</button>
        </form>
    `;
    document.getElementById('createTaskForm').addEventListener('submit', e => handleCreateTask(e, projectId));
}

function handleCreateTask(e, projectId) {
    e.preventDefault();
    const name = document.getElementById('taskName').value;
    const description = document.getElementById('taskDescription').value;
    createTask(projectId, { name, description })
        .then(() => loadTasks(projectId))
        .catch(error => console.error('Error creating task:', error));
}

function showAIAssistant(projectId) {
    app.innerHTML += `
        <h3>AI Assistant</h3>
        <textarea id="aiQuery" placeholder="Ask the AI a question about your project"></textarea>
        <button onclick="handleAskAI(${projectId})">Ask AI</button>
        <div id="aiResponse"></div>
    `;
}

function handleAskAI(projectId) {
    const query = document.getElementById('aiQuery').value;
    askAI(projectId, query)
        .then(response => {
            document.getElementById('aiResponse').innerHTML = `<p>${response}</p>`;
        })
        .catch(error => console.error('Error asking AI:', error));
}

// Make functions global so they can be called from inline onclick handlers
window.loadTasks = loadTasks;
window.showCreateTaskForm = showCreateTaskForm;
window.showAIAssistant = showAIAssistant;
window.handleAskAI = handleAskAI;