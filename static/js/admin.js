// CAVE-Plus Admin Dashboard
class AdminDashboard {
    constructor() {
        this.ws = null;
        this.adminName = '';
        this.password = '';
        this.loginState = 'name';
        this.currentInput = '';
        
        this.initElements();
        this.initEventListeners();
    }
    
    initElements() {
        // Screens
        this.loginScreen = document.getElementById('login-screen');
        this.adminScreen = document.getElementById('admin-screen');
        
        // Login
        this.loginDisplay = document.getElementById('login-display');
        this.nameInput = document.getElementById('name-input');
        
        // Dashboard
        this.adminNameSpan = document.getElementById('admin-name');
        this.playerCount = document.getElementById('player-count');
        this.playersTbody = document.getElementById('players-tbody');
        this.objectsTbody = document.getElementById('objects-tbody');
        this.creaturesTbody = document.getElementById('creatures-tbody');
        
        // Controls
        this.lightsToggle = document.getElementById('lights-toggle');
        this.portcullisToggle = document.getElementById('portcullis-toggle');
        this.activityInput = document.getElementById('activity-input');
        this.activitySet = document.getElementById('activity-set');
        this.staffInput = document.getElementById('staff-input');
        this.staffSet = document.getElementById('staff-set');
        this.logoutBtn = document.getElementById('logout-btn');
    }
    
    initEventListeners() {
        // Login keyboard
        document.addEventListener('keydown', (e) => {
            if (this.loginScreen.classList.contains('active')) {
                this.handleLoginKey(e);
            }
        });
        
        // Control buttons
        this.lightsToggle.addEventListener('click', () => this.toggleLights());
        this.portcullisToggle.addEventListener('click', () => this.togglePortcullis());
        this.activitySet.addEventListener('click', () => this.setActivity());
        this.staffSet.addEventListener('click', () => this.setStaff());
        this.logoutBtn.addEventListener('click', () => this.logout());
    }
    
    handleLoginKey(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (this.loginState === 'name') {
                if (this.currentInput.length >= 2) {
                    this.adminName = this.currentInput.toUpperCase().replace(/[^A-Z]/g, '');
                    if (this.adminName.length < 2) {
                        this.currentInput = '';
                        this.updateLoginDisplay();
                        return;
                    }
                    this.currentInput = '';
                    this.loginState = 'password';
                    this.updateLoginDisplay();
                }
            } else if (this.loginState === 'password') {
                if (this.currentInput.length >= 4) {
                    this.password = this.currentInput;
                    this.connect();
                } else {
                    this.showLoginError('Password too short!');
                }
            }
        } else if (e.key === 'Backspace') {
            e.preventDefault();
            this.currentInput = this.currentInput.slice(0, -1);
            this.updateLoginDisplay();
        } else if (e.key.length === 1 && !e.ctrlKey && !e.altKey && !e.metaKey) {
            e.preventDefault();
            if (this.currentInput.length < 20) {
                this.currentInput += e.key;
            }
            this.updateLoginDisplay();
        }
    }
    
    updateLoginDisplay() {
        if (this.loginState === 'name') {
            this.loginDisplay.innerHTML = `<p>Please enter your name: ${this.currentInput}<span class="cursor">_</span></p>`;
        } else if (this.loginState === 'password') {
            this.loginDisplay.innerHTML = `<p>Please enter your name: ${this.adminName}</p><p>Enter password: <span class="cursor">_</span></p>`;
        }
    }
    
    showLoginError(message) {
        this.loginDisplay.innerHTML = `<p style="color: #ff0000;">${message}</p><p>Press any key to try again...</p>`;
        this.currentInput = '';
        const resetLogin = (e) => {
            document.removeEventListener('keydown', resetLogin);
            this.loginState = 'name';
            this.adminName = '';
            this.password = '';
            this.updateLoginDisplay();
        };
        document.addEventListener('keydown', resetLogin);
    }
    
    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/admin/${encodeURIComponent(this.adminName)}`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            // Send password for authentication
            this.ws.send(JSON.stringify({
                password: this.password
            }));
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showLoginError('Connection error');
        };
        
        this.ws.onclose = () => {
            if (this.adminScreen.classList.contains('active')) {
                alert('Connection lost. Please refresh.');
            }
        };
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'error':
                this.showLoginError(data.message);
                break;
                
            case 'auth_success':
                this.showDashboard();
                break;
                
            case 'game_state':
                this.updateGameState(data);
                break;
        }
    }
    
    showDashboard() {
        this.loginScreen.classList.remove('active');
        this.adminScreen.classList.add('active');
        this.adminNameSpan.textContent = `Admin: ${this.adminName}`;
    }
    
    updateGameState(data) {
        // Update players
        this.updatePlayers(data.players);
        
        // Update environment
        this.updateEnvironment(data.environment);
        
        // Update objects
        this.updateObjects(data.objects);
        
        // Update creatures
        this.updateCreatures(data.creatures);
    }
    
    updatePlayers(players) {
        this.playerCount.textContent = players.length;
        
        if (players.length === 0) {
            this.playersTbody.innerHTML = '<tr><td colspan="8" class="empty">No players connected</td></tr>';
            return;
        }
        
        this.playersTbody.innerHTML = players.map(player => `
            <tr>
                <td>${player.name}</td>
                <td>${player.rank}</td>
                <td>${player.room_id}</td>
                <td>${player.stamina}/${player.max_stamina}</td>
                <td>${player.score}</td>
                <td>${player.inventory.join(', ') || 'None'}</td>
                <td><span class="status-badge ${player.is_disconnected ? 'status-disconnected' : 'status-connected'}">
                    ${player.is_disconnected ? 'Disconnected' : 'Connected'}
                </span></td>
                <td>
                    <button class="action-btn kick-btn" onclick="admin.kickPlayer('${player.name}')">Kick</button>
                </td>
            </tr>
        `).join('');
    }
    
    updateEnvironment(env) {
        // Lights
        this.lightsToggle.textContent = env.lights_on ? 'ON' : 'OFF';
        this.lightsToggle.className = env.lights_on ? 'toggle-btn on' : 'toggle-btn off';
        
        // Portcullis
        this.portcullisToggle.textContent = env.portcullis_up ? 'UP' : 'DOWN';
        this.portcullisToggle.className = env.portcullis_up ? 'toggle-btn on' : 'toggle-btn off';
        
        // Activity
        this.activityInput.value = env.activity_level;
        
        // Staff
        this.staffInput.value = env.staff_charges;
    }
    
    updateObjects(objects) {
        if (objects.length === 0) {
            this.objectsTbody.innerHTML = '<tr><td colspan="3" class="empty">No objects</td></tr>';
            return;
        }
        
        this.objectsTbody.innerHTML = objects.map(obj => `
            <tr>
                <td>${obj.name}</td>
                <td>Room ${obj.room_id}</td>
                <td>${obj.held_by || 'None'}</td>
            </tr>
        `).join('');
    }
    
    updateCreatures(creatures) {
        if (creatures.length === 0) {
            this.creaturesTbody.innerHTML = '<tr><td colspan="4" class="empty">No creatures</td></tr>';
            return;
        }
        
        this.creaturesTbody.innerHTML = creatures.map(creature => `
            <tr>
                <td>${creature.name}</td>
                <td>${creature.room_id}</td>
                <td>${creature.stamina}/${creature.max_stamina}</td>
                <td>${creature.behavior === 'A' ? 'Aggressive' : 'Passive'}</td>
            </tr>
        `).join('');
    }
    
    // Control actions
    toggleLights() {
        this.sendCommand('toggle_lights');
    }
    
    togglePortcullis() {
        this.sendCommand('toggle_portcullis');
    }
    
    setActivity() {
        const value = parseInt(this.activityInput.value);
        if (value >= 0 && value <= 9) {
            this.sendCommand('set_activity', { value });
        } else {
            alert('Activity must be between 0 and 9');
        }
    }
    
    setStaff() {
        const value = parseInt(this.staffInput.value);
        if (value >= 0 && value <= 127) {
            this.sendCommand('set_staff', { value });
        } else {
            alert('Staff charges must be between 0 and 127');
        }
    }
    
    kickPlayer(playerName) {
        if (confirm(`Kick ${playerName} from the game?`)) {
            this.sendCommand('kick_player', { player_name: playerName });
        }
    }
    
    sendCommand(command, data = {}) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                command,
                ...data
            }));
        }
    }
    
    logout() {
        if (this.ws) {
            this.ws.close();
        }
        location.reload();
    }
}

// Initialize admin dashboard
const admin = new AdminDashboard();
