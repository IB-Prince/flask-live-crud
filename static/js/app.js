// API Testing Functions
function testEndpoint(url) {
    fetch(url)
        .then(response => response.json())
        .then(data => {
            document.getElementById('apiResponse').textContent = JSON.stringify(data, null, 2);
            document.getElementById('apiResults').style.display = 'block';
            document.getElementById('apiResults').scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => {
            document.getElementById('apiResponse').textContent = 'Error: ' + error.message;
            document.getElementById('apiResults').style.display = 'block';
        });
}

function testGetUser() {
    const userId = document.getElementById('userId').value;
    if (!userId) {
        alert('Please enter a user ID');
        return;
    }
    testEndpoint(`/users/${userId}`);
}

function createUser() {
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    
    if (!username || !email) {
        alert('Please fill in all fields');
        return;
    }
    
    fetch('/users', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('apiResponse').textContent = JSON.stringify(data, null, 2);
        document.getElementById('apiResults').style.display = 'block';
        document.getElementById('createUserForm').reset();
        bootstrap.Modal.getInstance(document.getElementById('createUserModal')).hide();
        
        // Reload users if on users page
        if (typeof loadUsers === 'function') {
            loadUsers();
        }
    })
    .catch(error => {
        alert('Error creating user: ' + error.message);
    });
}

// Users page functions
function loadUsers() {
    fetch('/users')
        .then(response => response.json())
        .then(data => {
            displayUsers(data.users || []);
        })
        .catch(error => {
            document.getElementById('usersTable').innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error loading users: ${error.message}
                </div>
            `;
        });
}

function displayUsers(users) {
    const usersTable = document.getElementById('usersTable');
    
    if (users.length === 0) {
        usersTable.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-users fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">No users found</h5>
                <p class="text-muted">Create your first user to get started!</p>
            </div>
        `;
        return;
    }
    
    let html = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead class="table-dark">
                    <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    users.forEach(user => {
        html += `
            <tr>
                <td><span class="badge bg-primary">${user.id}</span></td>
                <td><strong>${user.username}</strong></td>
                <td>${user.email}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-2" onclick="editUser(${user.id}, '${user.username}', '${user.email}')">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteUser(${user.id})">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    usersTable.innerHTML = html;
}

function editUser(id, username, email) {
    document.getElementById('editUserId').value = id;
    document.getElementById('editUsername').value = username;
    document.getElementById('editEmail').value = email;
    new bootstrap.Modal(document.getElementById('editUserModal')).show();
}

function updateUser() {
    const id = document.getElementById('editUserId').value;
    const username = document.getElementById('editUsername').value;
    const email = document.getElementById('editEmail').value;
    
    fetch(`/users/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email })
    })
    .then(response => response.json())
    .then(data => {
        bootstrap.Modal.getInstance(document.getElementById('editUserModal')).hide();
        loadUsers();
        showAlert('User updated successfully!', 'success');
    })
    .catch(error => {
        showAlert('Error updating user: ' + error.message, 'danger');
    });
}

function deleteUser(id) {
    if (!confirm('Are you sure you want to delete this user?')) {
        return;
    }
    
    fetch(`/users/${id}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        loadUsers();
        showAlert('User deleted successfully!', 'success');
    })
    .catch(error => {
        showAlert('Error deleting user: ' + error.message, 'danger');
    });
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.querySelector('main').insertBefore(alertDiv, document.querySelector('main').firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Test endpoint buttons
    document.querySelectorAll('.test-endpoint').forEach(button => {
        button.addEventListener('click', function() {
            testEndpoint(this.dataset.url);
        });
    });
});