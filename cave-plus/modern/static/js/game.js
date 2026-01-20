// Cave-Plus Web Client
class CaveGame {
    constructor() {
        this.ws = null;
        this.playerName = '';
        this.commandHistory = [];
        this.historyIndex = -1;
        this.statusMessages = []; // Array to hold status messages
        this.maxStatusMessages = 6; // Max 6 lines in status area
        
        this.initElements();
        this.initEventListeners();
    }
    
    initElements() {
        // Screens
        this.loginScreen = document.getElementById('login-screen');
        this.gameScreen = document.getElementById('game-screen');
        
        // Login
        this.loginForm = document.getElementById('login-form');
        this.playerNameInput = document.getElementById('player-name');
        
        // Game UI
        this.messageLog = document.getElementById('message-log');
        this.commandInput = document.getElementById('command-input');
        this.statusMessagesElement = document.getElementById('status-messages');
        
        // Player state (tracked internally)
        this.playerData = {
            name: '',
            rank: '',
            stamina: 0,
            max_stamina: 0,
            score: 0,
            inventory: []
        };
    }
    
    initEventListeners() {
        // Login form
        this.loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.login();
        });
        
        // Command input
        this.commandInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.sendCommand();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.navigateHistory(-1);
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                this.navigateHistory(1);
            }
        });
    }
    
    login() {
        this.playerName = this.playerNameInput.value.trim();
        const password = document.getElementById('player-password').value.trim();
        
        if (!this.playerName || this.playerName.length < 2) {
            alert('Please enter a name (at least 2 characters)');
            return;
        }
        
        if (!password || password.length < 4) {
            alert('Password must be at least 4 characters');
            return;
        }
        
        this.password = password;
        this.connect();
    }
    
    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${encodeURIComponent(this.playerName)}`;
        
        this.addMessage('Connecting to server...', 'system');
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            this.addMessage('Connected! Authenticating...', 'system');
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
            this.addMessage('Connection error!', 'error');
            console.error('WebSocket error:', error);
        };
        
        this.ws.onclose = () => {
            this.addMessage('Disconnected from server.', 'system');
            setTimeout(() => {
                this.showLogin();
            }, 2000);
        };
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'welcome':
                this.showGame();
                this.addMessage(data.message, 'system');
                this.updatePlayer(data.player);
                break;
                
            case 'room':
                // Pass creatures from data
                const roomData = {
                    ...data.room,
                    creatures: data.creatures || []
                };
                this.updateRoom(roomData, data.players, data.objects);
                this.updatePlayer(data.player);
                break;
                
            case 'message':
                const text = data.text;
                const style = data.style || 'normal';
                
                // Combat and important messages go to status area ONLY
                if (style === 'combat' || style === 'death' || style === 'action') {
                    this.addStatusMessage(text);
                } else {
                    // Other messages go to main log
                    this.addMessage(text, style);
                }
                break;
                
            case 'inventory':
                // Update inventory count
                if (this.playerData) {
                    this.playerData.inventory = data.items || [];
                }
                break;
                
            case 'error':
                this.addMessage(data.message, 'error');
                break;
        }
    }
    
    updateRoom(room, players, objects) {
        // Build room description (matching BBC Micro - no room number)
        let desc = room.description;
        
        // Add objects (one per line with A/An)
        if (objects && objects.length > 0) {
            desc += '\n';
            for (const obj of objects) {
                desc += `\n${this.addArticle(obj)} is here.`;
            }
        }
        
        // Add creatures (one per line with A/An)
        if (room.creatures && room.creatures.length > 0) {
            desc += '\n';
            for (const creature of room.creatures) {
                desc += `\n${this.addArticle(creature.name)} is here.`;
            }
        }
        
        // Add players (one per line)
        if (players && players.length > 0) {
            desc += '\n';
            for (const playerName of players) {
                desc += `\n${playerName} is here`;
            }
        }
        
        this.addMessage(desc, 'normal');
    }
    
    addArticle(name) {
        // Add 'A' or 'An' before a name based on first letter
        const vowels = 'AEIOU';
        const firstLetter = name[0].toUpperCase();
        const article = vowels.includes(firstLetter) ? 'An' : 'A';
        return `${article} ${name}`;
    }
    
    updatePlayer(player) {
        // Store player data internally
        this.playerData = {
            name: player.name,
            rank: player.rank,
            stamina: player.stamina,
            max_stamina: player.max_stamina,
            score: player.score,
            inventory: player.inventory
        };
        
        // Don't display stats in status area - it's for messages only
    }
    
    addStatusMessage(text) {
        // Add message to status array
        this.statusMessages.push(text);
        
        // Keep only the last N messages (6 rows available)
        if (this.statusMessages.length > this.maxStatusMessages) {
            this.statusMessages.shift(); // Remove oldest
        }
        
        // Display all messages
        this.statusMessagesElement.textContent = this.statusMessages.join('\n');
        
        // Auto-scroll to bottom
        this.statusMessagesElement.scrollTop = this.statusMessagesElement.scrollHeight;
    }
    
    addMessage(text, style = 'normal') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${style}`;
        messageDiv.textContent = text;
        
        this.messageLog.appendChild(messageDiv);
        this.messageLog.scrollTop = this.messageLog.scrollHeight;
    }
    
    sendCommand() {
        const command = this.commandInput.value.trim();
        
        if (!command) {
            return;
        }
        
        // Add to history
        this.commandHistory.push(command);
        this.historyIndex = this.commandHistory.length;
        
        // Echo command
        this.addMessage(`> ${command}`, 'normal');
        
        // Send to server
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                command: command
            }));
        }
        
        // Clear input
        this.commandInput.value = '';
    }
    
    navigateHistory(direction) {
        if (this.commandHistory.length === 0) {
            return;
        }
        
        this.historyIndex += direction;
        
        if (this.historyIndex < 0) {
            this.historyIndex = 0;
        } else if (this.historyIndex >= this.commandHistory.length) {
            this.historyIndex = this.commandHistory.length;
            this.commandInput.value = '';
            return;
        }
        
        this.commandInput.value = this.commandHistory[this.historyIndex];
    }
    
    showLogin() {
        this.loginScreen.classList.add('active');
        this.gameScreen.classList.remove('active');
        this.playerNameInput.focus();
    }
    
    showGame() {
        this.loginScreen.classList.remove('active');
        this.gameScreen.classList.add('active');
        this.commandInput.focus();
    }
}

// Initialize game when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.game = new CaveGame();
});
