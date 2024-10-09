const API_URL = 'http://localhost:8000/api/v1';

async function fetchProjects() {
    try {
        const response = await fetch(`${API_URL}/projects/`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const projects = await response.json();
        updateProjectLists(projects);
    } catch (error) {
        console.error('Error fetching projects:', error);
        alert('Failed to fetch projects. Check the console for details.');
    }
}

function updateProjectLists(projects) {
    const projectList = document.getElementById('projectList');
    const projectSelects = ['projectSelect', 'aiProjectSelect', 'reportProjectSelect', 'projectSelectForTeam'];
    
    projectList.innerHTML = '';
    projectSelects.forEach(selectId => {
        const select = document.getElementById(selectId);
        select.innerHTML = '<option value="">Select a project</option>';
    });
    
    projects.forEach(project => {
        const teamMembers = project.team_members.map(tm => tm.name).join(', ');
        projectList.innerHTML += `
            <li>
                ${project.name}: ${project.description}
                <br>Team Members: ${teamMembers || 'None'}
            </li>`;
        projectSelects.forEach(selectId => {
            const select = document.getElementById(selectId);
            select.innerHTML += `<option value="${project.id}">${project.name}</option>`;
        });
    });
}

async function createProject() {
    const name = document.getElementById('projectName').value;
    const description = document.getElementById('projectDescription').value;
    
    try {
        const response = await fetch(`${API_URL}/projects/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Project created:', result);
        
        fetchProjects();
        document.getElementById('projectName').value = '';
        document.getElementById('projectDescription').value = '';
    } catch (error) {
        console.error('Error creating project:', error);
        alert('Failed to create project. Check the console for details.');
    }
}

async function fetchTasks(projectId) {
    try {
        const response = await fetch(`${API_URL}/projects/${projectId}/tasks/`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const tasks = await response.json();
        updateTaskList(tasks);
    } catch (error) {
        console.error('Error fetching tasks:', error);
        alert('Failed to fetch tasks. Check the console for details.');
    }
}

function updateTaskList(tasks) {
    const taskList = document.getElementById('taskList');
    const taskSelect = document.getElementById('taskSelect');
    
    taskList.innerHTML = '';
    taskSelect.innerHTML = '<option value="">Select a task</option>';
    
    tasks.forEach(task => {
        taskList.innerHTML += `<li>${task.title}: ${task.status} (Skills: ${task.required_skills ? task.required_skills.join(', ') : 'None'})</li>`;
        taskSelect.innerHTML += `<option value="${task.id}">${task.title}</option>`;
    });
}

async function createTask() {
    const projectId = document.getElementById('projectSelect').value;
    const title = document.getElementById('taskTitle').value;
    const description = document.getElementById('taskDescription').value;
    const skills = document.getElementById('taskSkills').value.split(',').map(skill => skill.trim());
    
    if (!projectId) {
        alert('Please select a project first.');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/projects/${projectId}/tasks/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description, required_skills: skills })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Task created:', result);
        
        fetchTasks(projectId);
        document.getElementById('taskTitle').value = '';
        document.getElementById('taskDescription').value = '';
        document.getElementById('taskSkills').value = '';
    } catch (error) {
        console.error('Error creating task:', error);
        alert('Failed to create task. Check the console for details.');
    }
}

async function fetchTeamMembers() {
    console.log('Fetching team members...');
    try {
        const response = await fetch(`${API_URL}/team-members/`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const teamMembers = await response.json();
        console.log('Received team members:', teamMembers);
        updateTeamMemberList(teamMembers);
    } catch (error) {
        console.error('Error fetching team members:', error);
        alert('Failed to fetch team members. Check the console for details.');
    }
}

function updateTeamMemberList(teamMembers) {
    console.log('Updating team member list with:', teamMembers);
    const teamMemberList = document.getElementById('teamMemberList');
    const teamMemberSelect = document.getElementById('teamMemberSelect');
    
    teamMemberList.innerHTML = '';
    teamMemberSelect.innerHTML = '<option value="">Select a team member</option>';
    
    teamMembers.forEach(member => {
        teamMemberList.innerHTML += `<li>${member.name}: ${member.skills.join(', ')}</li>`;
        teamMemberSelect.innerHTML += `<option value="${member.id}">${member.name}</option>`;
    });
    console.log('Team member list updated');
}

async function createTeamMember() {
    console.log("createTeamMember function called");
    const name = document.getElementById('teamMemberName').value;
    const email = document.getElementById('teamMemberEmail').value;
    const skills = document.getElementById('teamMemberSkills').value.split(',').map(skill => skill.trim());
    
    console.log("Sending team member data:", { name, email, skills });
    
    try {
        const response = await fetch(`${API_URL}/team-members/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, skills, role: null })  // Include role, even if it's null
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`HTTP error! status: ${response.status}, message: ${JSON.stringify(errorData)}`);
        }
        
        const result = await response.json();
        console.log('Team member created:', result);
        
        console.log('About to fetch team members');
        await fetchTeamMembers();
        console.log('Finished fetching team members');
        
        document.getElementById('teamMemberName').value = '';
        document.getElementById('teamMemberEmail').value = '';
        document.getElementById('teamMemberSkills').value = '';
    } catch (error) {
        console.error('Error creating team member:', error);
        alert('Failed to create team member. Check the console for details.');
    }
}

async function assignTeamMemberToProject() {
    const projectId = document.getElementById('projectSelectForTeam').value;
    const teamMemberId = document.getElementById('teamMemberSelect').value;
    
    if (!projectId || !teamMemberId) {
        alert('Please select both a project and a team member.');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/projects/${projectId}/team-members/${teamMemberId}`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Team member assigned to project:', result);
        alert('Team member assigned to project successfully.');
        
        // Refresh the project list to show the updated team members
        await fetchProjects();
    } catch (error) {
        console.error('Error assigning team member to project:', error);
        alert('Failed to assign team member to project. Check the console for details.');
    }
}

async function askAI() {
    const projectId = document.getElementById('aiProjectSelect').value;
    const question = document.getElementById('aiQuestion').value;
    
    if (!projectId) {
        alert('Please select a project first.');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/projects/${projectId}/ai-chat/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        document.getElementById('aiResponse').innerText = result.answer;
    } catch (error) {
        console.error('Error asking AI:', error);
        alert('Failed to get AI response. Check console for details.');
    }
}

async function prioritizeTask() {
    const taskId = document.getElementById('taskSelect').value;
    const projectId = document.getElementById('projectSelect').value;
    
    if (!taskId || !projectId) {
        alert('Please select a project and a task first.');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/projects/${projectId}/tasks/${taskId}/prioritize/`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        document.getElementById('taskActions').innerText = `Task prioritized: ${result.priority}`;
        fetchTasks(projectId);
    } catch (error) {
        console.error('Error prioritizing task:', error);
        alert('Failed to prioritize task. Check console for details.');
    }
}

async function getSuggestions() {
    const taskId = document.getElementById('taskSelect').value;
    const projectId = document.getElementById('projectSelect').value;
    
    if (!taskId || !projectId) {
        alert('Please select a project and a task first.');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/projects/${projectId}/tasks/${taskId}/suggest/`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        document.getElementById('taskActions').innerHTML = `
            <h3>Suggestions:</h3>
            <ul>${result.suggestions.map(s => `<li>${s}</li>`).join('')}</ul>
            <h3>Resources:</h3>
            <ul>${result.resources.map(r => `<li>${r}</li>`).join('')}</ul>
        `;
    } catch (error) {
        console.error('Error getting suggestions:', error);
        alert('Failed to get suggestions. Check console for details.');
    }
}

async function generateReport() {
    const projectId = document.getElementById('reportProjectSelect').value;
    
    if (!projectId) {
        alert('Please select a project first.');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/projects/${projectId}/report/`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        document.getElementById('projectReport').innerHTML = `
            <h3>Summary:</h3>
            <p>${result.summary}</p>
            <h3>Key Metrics:</h3>
            <ul>${Object.entries(result.key_metrics).map(([k, v]) => `<li>${k}: ${v}</li>`).join('')}</ul>
            <h3>Recommendations:</h3>
            <ul>${result.recommendations.map(r => `<li>${r}</li>`).join('')}</ul>
        `;
    } catch (error) {
        console.error('Error generating report:', error);
        alert('Failed to generate report. Check console for details.');
    }
}

// Event listeners
document.getElementById('projectSelect').addEventListener('change', (e) => {
    if (e.target.value) {
        fetchTasks(e.target.value);
    }
});

// Initial load
fetchProjects();
fetchTeamMembers();