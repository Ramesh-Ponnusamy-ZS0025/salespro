const API_URL = 'http://localhost:8001/api';

// DOM Elements
const loginSection = document.getElementById('loginSection');
const registerSection = document.getElementById('registerSection');
const dashboardSection = document.getElementById('dashboardSection');
const messageDiv = document.getElementById('message');

const loginEmail = document.getElementById('loginEmail');
const loginPassword = document.getElementById('loginPassword');
const loginBtn = document.getElementById('loginBtn');

const registerEmail = document.getElementById('registerEmail');
const registerPassword = document.getElementById('registerPassword');
const registerBtn = document.getElementById('registerBtn');

const showRegisterBtn = document.getElementById('showRegister');
const showLoginBtn = document.getElementById('showLogin');
const logoutBtn = document.getElementById('logoutBtn');

const userEmail = document.getElementById('userEmail');
const contentCount = document.getElementById('contentCount');

// Show message
function showMessage(message, type = 'error') {
  messageDiv.textContent = message;
  messageDiv.className = `message ${type}`;
  messageDiv.classList.remove('hidden');
  setTimeout(() => {
    messageDiv.classList.add('hidden');
  }, 3000);
}

// Check if user is logged in
async function checkAuth() {
  const token = await chrome.storage.local.get(['authToken']);
  
  if (token.authToken) {
    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token.authToken}`
        }
      });
      
      if (response.ok) {
        const user = await response.json();
        showDashboard(user);
        loadStats();
      } else {
        showLogin();
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      showLogin();
    }
  } else {
    showLogin();
  }
}

// Show login form
function showLogin() {
  loginSection.classList.remove('hidden');
  registerSection.classList.add('hidden');
  dashboardSection.classList.add('hidden');
}

// Show register form
function showRegister() {
  loginSection.classList.add('hidden');
  registerSection.classList.remove('hidden');
  dashboardSection.classList.add('hidden');
}

// Show dashboard
function showDashboard(user) {
  loginSection.classList.add('hidden');
  registerSection.classList.add('hidden');
  dashboardSection.classList.remove('hidden');
  userEmail.textContent = user.email;
}

// Login
async function login() {
  const email = loginEmail.value.trim();
  const password = loginPassword.value;
  
  if (!email || !password) {
    showMessage('Please fill in all fields');
    return;
  }
  
  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password })
    });
    
    if (response.ok) {
      const data = await response.json();
      await chrome.storage.local.set({ authToken: data.access_token });
      showMessage('Login successful!', 'success');
      checkAuth();
    } else {
      const error = await response.json();
      showMessage(error.detail || 'Login failed');
    }
  } catch (error) {
    showMessage('Network error. Please try again.');
  }
}

// Register
async function register() {
  const email = registerEmail.value.trim();
  const password = registerPassword.value;
  
  if (!email || !password) {
    showMessage('Please fill in all fields');
    return;
  }
  
  if (password.length < 6) {
    showMessage('Password must be at least 6 characters');
    return;
  }
  
  try {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password })
    });
    
    if (response.ok) {
      const data = await response.json();
      await chrome.storage.local.set({ authToken: data.access_token });
      showMessage('Account created successfully!', 'success');
      checkAuth();
    } else {
      const error = await response.json();
      showMessage(error.detail || 'Registration failed');
    }
  } catch (error) {
    showMessage('Network error. Please try again.');
  }
}

// Logout
async function logout() {
  await chrome.storage.local.remove(['authToken']);
  showLogin();
  showMessage('Logged out successfully', 'success');
}

// Load stats
async function loadStats() {
  const token = await chrome.storage.local.get(['authToken']);
  
  if (token.authToken) {
    try {
      const response = await fetch(`${API_URL}/content-history?limit=100`, {
        headers: {
          'Authorization': `Bearer ${token.authToken}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        contentCount.textContent = data.length;
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  }
}

// Event listeners
loginBtn.addEventListener('click', login);
registerBtn.addEventListener('click', register);
showRegisterBtn.addEventListener('click', showRegister);
showLoginBtn.addEventListener('click', showLogin);
logoutBtn.addEventListener('click', logout);

// Enter key support
loginPassword.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') login();
});

registerPassword.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') register();
});

// Initialize
checkAuth();