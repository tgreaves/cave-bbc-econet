// Cave-Plus Web Client v1.1
class CaveGame {
    constructor() {
        this.ws = null;
        this.playerName = '';
        this.password = '';
        this.commandHistory = [];
        this.historyIndex = -1;
        this.statusMessages = []; // Array to hold status messages
        this.maxStatusMessages = 6; // Max 6 lines in status area
        
        // Login state
        this.loginState = 'name'; // 'name' or 'password'
        this.currentInput = '';
        
        this.initElements();
        this.initEventListeners();
    }
    
    initElements() {
        // Screens
        this.loginScreen = document.getElementById('login-screen');
        this.gameScreen = document.getElementById('game-screen');
        
        // Login
        this.loginDisplay = document.getElementById('login-display');
        this.nameInputSpan = document.getElementById('name-input');
        
        // Game UI
        this.messageLog = document.getElementById('message-log');
        this.commandInput = document.getElementById('command-input');
        this.statusMessagesElement = document.getElementById('status-messages');
        this.commandPrompt = document.getElementById('command-prompt');
        
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
        // Keyboard input for login
        document.addEventListener('keydown', (e) => {
            if (this.loginScreen.classList.contains('active')) {
                this.handleLoginKey(e);
            }
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
            } else if (e.key.length === 1 && !e.ctrlKey && !e.altKey && !e.metaKey) {
                // BBC Micro behavior: convert to uppercase immediately as typed
                e.preventDefault();
                const char = e.key.toUpperCase();
                // Insert at cursor position
                const start = this.commandInput.selectionStart;
                const end = this.commandInput.selectionEnd;
                const value = this.commandInput.value;
                this.commandInput.value = value.substring(0, start) + char + value.substring(end);
                this.commandInput.selectionStart = this.commandInput.selectionEnd = start + 1;
            }
        });
    }
    
    handleLoginKey(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (this.loginState === 'name') {
                if (this.currentInput.length >= 2) {
                    // Apply BBC Micro FNB function: uppercase, letters only
                    this.playerName = this.currentInput.toUpperCase().replace(/[^A-Z]/g, '');
                    if (this.playerName.length < 2) {
                        // After filtering, name is too short
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
                    this.showLoginError('That is too short !');
                }
            }
        } else if (e.key === 'Backspace') {
            e.preventDefault();
            this.currentInput = this.currentInput.slice(0, -1);
            this.updateLoginDisplay();
        } else if (e.key.length === 1 && !e.ctrlKey && !e.altKey && !e.metaKey) {
            e.preventDefault();
            if (this.loginState === 'name' && this.currentInput.length < 20) {
                this.currentInput += e.key;
            } else if (this.loginState === 'password' && this.currentInput.length < 20) {
                this.currentInput += e.key;
            }
            this.updateLoginDisplay();
        }
    }
    
    updateLoginDisplay() {
        if (this.loginState === 'name') {
            this.loginDisplay.innerHTML = `<span style="color: #ffff00;">CAVE-PLUS</span> <span style="color: #ffffff;">(C) 2026</span>

<span style="color: #ffff00;">From CAVE</span> <span style="color: #ffffff;">(C)</span> <span style="color: #00ffff;">GJL WOTWECP</span> <span style="color: #ffffff;">1985</span>


<span style="color: #ffffff;">Please enter your name : ${this.currentInput}<span class="cursor">_</span></span>`;
        } else if (this.loginState === 'password') {
            // Password is NOT shown (VDU21 disabled output in original)
            this.loginDisplay.innerHTML = `<span style="color: #ffff00;">CAVE-PLUS</span> <span style="color: #ffffff;">(C) 2026</span>

<span style="color: #ffff00;">From CAVE</span> <span style="color: #ffffff;">(C)</span> <span style="color: #00ffff;">GJL WOTWECP</span> <span style="color: #ffffff;">1985</span>


<span style="color: #ffffff;">Please enter your name : ${this.playerName}</span>

<span style="color: #ffffff;">Enter your password ${this.playerName} : <span class="cursor">_</span></span>`;
        }
    }
    
    showLoginError(message) {
        this.loginDisplay.innerHTML = `<span style="color: #ffff00;">CAVE-PLUS</span> <span style="color: #ffffff;">(C) 2026</span>

<span style="color: #ffff00;">From CAVE</span> <span style="color: #ffffff;">(C)</span> <span style="color: #00ffff;">GJL WOTWECP</span> <span style="color: #ffffff;">1985</span>


<span style="color: #ffffff;">Please enter your name : ${this.playerName}</span>

<span style="color: #ffffff;">Enter your password ${this.playerName} : </span>

<span style="color: #ffffff;">${message}</span>

<span style="color: #ffffff;">Enter your password ${this.playerName} : <span class="cursor">_</span></span>`;
        this.currentInput = '';
    }
    
    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${encodeURIComponent(this.playerName)}`;
        
        // Don't show any messages - just connect silently like BBC Micro
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            // Send password for authentication (silently)
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
        };
        
        this.ws.onclose = () => {
            // Silently reset to login on disconnect
            setTimeout(() => {
                this.showLogin();
            }, 1000);
        };
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'error':
                // If still on login screen, show error there
                if (this.loginScreen.classList.contains('active')) {
                    this.loginDisplay.innerHTML = `<span style="color: #ffff00;">CAVE-PLUS</span> <span style="color: #ffffff;">(C) 2026</span>

<span style="color: #ffff00;">From CAVE</span> <span style="color: #ffffff;">(C)</span> <span style="color: #00ffff;">GJL WOTWECP</span> <span style="color: #ffffff;">1985</span>


<span style="color: #ff0000;">${data.message}</span>

<span style="color: #ffffff;">Press any key to try again...</span>`;
                    
                    // Reset login state
                    this.loginState = 'name';
                    this.currentInput = '';
                    this.playerName = '';
                    this.password = '';
                    
                    // Wait for keypress then reset
                    const resetLogin = (e) => {
                        document.removeEventListener('keydown', resetLogin);
                        this.updateLoginDisplay();
                    };
                    document.addEventListener('keydown', resetLogin);
                } else {
                    this.addMessage(data.message, 'error');
                }
                break;
                
            case 'welcome':
                this.showGame();
                this.addMessage(data.message, 'system');
                // Show player list or "only caver" message
                if (data.player_list) {
                    this.addMessage(data.player_list, 'system');
                }
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
        
        // Update prompt based on rank (matching BBC Micro original)
        if (player.rank === 'Wizard') {
            this.commandPrompt.textContent = '____*';
        } else {
            this.commandPrompt.textContent = '*';
        }
        
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
        let command = this.commandInput.value.trim();
        
        if (!command) {
            return;
        }
        
        // BBC Micro behavior: ensure command is uppercase
        command = command.toUpperCase();
        console.log('Sending command:', command); // Debug log
        
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
