// Cave-Plus Web Client v1.1
class CaveGame {
    constructor() {
        this.ws = null;
        this.playerName = '';
        this.password = '';
        this.commandHistory = [];
        this.historyIndex = -1;
        
        // Login state
        this.loginState = 'name'; // 'name' or 'password'
        this.currentInput = '';
        
        // CRT filter state (load from localStorage, default to ON)
        const savedFilter = localStorage.getItem('crtFilter');
        this.crtFilterEnabled = savedFilter === null ? true : savedFilter === 'true';
        
        // Sound state (load from localStorage, default to ON)
        const savedSound = localStorage.getItem('soundEnabled');
        this.soundEnabled = savedSound === null ? true : savedSound === 'true';
        
        // Audio context for BBC Micro beep simulation
        this.audioContext = null;
        
        this.initElements();
        this.initEventListeners();
        this.applyCRTFilter();
        this.applySoundState();
    }
    
    initElements() {
        // Screens
        this.loginScreen = document.getElementById('login-screen');
        this.gameScreen = document.getElementById('game-screen');
        
        // Login
        this.loginDisplay = document.getElementById('login-display');
        this.nameInputSpan = document.getElementById('name-input');
        
        // Game UI - status area + scrolling message area with inline prompt
        this.statusMessagesElement = document.getElementById('status-messages');
        this.messageLog = document.getElementById('message-log');
        this.promptElement = document.getElementById('prompt');
        this.commandDisplay = document.getElementById('command-display');
        this.commandInput = document.getElementById('command-input');
        
        // CRT toggle button
        this.crtToggle = document.getElementById('crt-toggle');
        
        // Sound toggle button
        this.soundToggle = document.getElementById('sound-toggle');
        
        // Player state (tracked internally)
        this.playerData = {
            name: '',
            rank: '',
            stamina: 0,
            max_stamina: 0,
            score: 0,
            inventory: []
        };
        
        // Status messages array
        this.statusMessages = [];
        this.maxStatusMessages = 6; // Max 6 lines in status area
    }
    
    initEventListeners() {
        // CRT filter toggle
        if (this.crtToggle) {
            console.log('CRT toggle button found, adding listener');
            this.crtToggle.addEventListener('click', () => {
                console.log('CRT toggle clicked');
                this.toggleCRTFilter();
            });
        } else {
            console.error('CRT toggle button not found!');
        }
        
        // Sound toggle
        if (this.soundToggle) {
            console.log('Sound toggle button found, adding listener');
            this.soundToggle.addEventListener('click', () => {
                console.log('Sound toggle clicked');
                this.toggleSound();
            });
        } else {
            console.error('Sound toggle button not found!');
        }
        
        // Keyboard input for login
        document.addEventListener('keydown', (e) => {
            if (this.loginScreen.classList.contains('active')) {
                this.handleLoginKey(e);
            }
        });
        
        // Command input - hidden field captures keystrokes
        this.commandInput.addEventListener('input', (e) => {
            // Apply drunk typing effects if player is drunk
            if (this.playerData && this.playerData.vodka_level > 1) {
                const vodkaLevel = this.playerData.vodka_level;
                console.log('Drunk typing active! Vodka level:', vodkaLevel);
                let value = this.commandInput.value;
                
                // Random chance to replace last character with random letter
                // Based on line 1440: IFV>1ANDRND(25)-1<V A$=CHR$(64+RND(26))
                if (value.length > 0 && Math.random() * 25 < vodkaLevel) {
                    const randomLetter = String.fromCharCode(65 + Math.floor(Math.random() * 26)); // A-Z
                    console.log('Replacing last char with:', randomLetter);
                    value = value.slice(0, -1) + randomLetter;
                    this.commandInput.value = value;
                }
                
                // Random chance to delete last character
                // Based on line 1450: IFV>1ANDRND(25)-1<V A$=""
                if (value.length > 0 && Math.random() * 25 < vodkaLevel) {
                    console.log('Deleting last char');
                    value = value.slice(0, -1);
                    this.commandInput.value = value;
                }
            }
            
            // Update visible command display
            this.commandDisplay.textContent = this.commandInput.value.toUpperCase();
        });
        
        this.commandInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.sendCommand();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.navigateHistory(-1);
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                this.navigateHistory(1);
            }
        });
        
        // Keep focus on hidden input when game screen is active
        this.gameScreen.addEventListener('click', () => {
            if (this.gameScreen.classList.contains('active')) {
                this.commandInput.focus();
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
            this.loginDisplay.innerHTML = `<span class="double-height" style="color: #ffff00;">CAVE-PLUS</span><span style="color: #ffffff;">(C) XOB 1988 </span><span class="double-height" style="color: #ffffff;">Version 1.00</span>

<span class="double-height" style="color: #ffff00;">From CAVE</span><span style="color: #ffffff;">(C) GJL WOTWECP 1985</span>


<span style="color: #ffffff;">Please enter your name : ${this.currentInput}<span class="cursor">_</span></span>`;
        } else if (this.loginState === 'password') {
            // Password is NOT shown (VDU21 disabled output in original)
            this.loginDisplay.innerHTML = `<span class="double-height" style="color: #ffff00;">CAVE-PLUS</span><span style="color: #ffffff;">(C) XOB 1988 </span><span class="double-height" style="color: #ffffff;">Version 1.00</span>

<span class="double-height" style="color: #ffff00;">From CAVE</span><span style="color: #ffffff;">(C) GJL WOTWECP 1985</span>


<span style="color: #ffffff;">Please enter your name : ${this.playerName}</span>

<span style="color: #ffffff;">Enter your password ${this.playerName} : <span class="cursor">_</span></span>`;
        }
    }
    
    showLoginError(message) {
        this.loginDisplay.innerHTML = `<span class="double-height" style="color: #ffff00;">CAVE-PLUS</span><span style="color: #ffffff;">(C) XOB 1988 </span><span class="double-height" style="color: #ffffff;">Version 1.00</span>

<span class="double-height" style="color: #ffff00;">From CAVE</span><span style="color: #ffffff;">(C) GJL WOTWECP 1985</span>


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
            // Show Going screen on disconnect
            setTimeout(() => {
                this.showGoing();
            }, 500);
        };
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'disable_input':
                // Disable command input (used during QUIT sequence)
                this.commandInput.disabled = true;
                this.commandInput.style.opacity = '0.5';
                break;
            
            case 'disconnect':
                // Server is disconnecting us (QUIT command)
                // Show Going screen
                this.showGoing();
                break;
            
            case 'player_update':
                // Update player data (vodka level, poison status, etc.)
                console.log('Received player_update:', data.player);
                if (data.player) {
                    this.updatePlayer(data.player);
                    console.log('Updated playerData:', this.playerData);
                }
                break;
                
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
                const beeps = data.beeps || 0;
                
                // Play beep if specified (VDU7 simulation)
                if (beeps > 0) {
                    this.playBeep(beeps);
                }
                
                // Combat and important messages go to status area
                if (style === 'combat' || style === 'death' || style === 'action') {
                    this.addStatusMessage(text);
                } else {
                    // Other messages go to main scrolling log
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
        console.log('updatePlayer called with:', player);
        // Store player data internally (including vodka_level for drunk typing)
        this.playerData = {
            name: player.name,
            rank: player.rank,
            stamina: player.stamina,
            max_stamina: player.max_stamina,
            score: player.score,
            inventory: player.inventory,
            vodka_level: player.vodka_level || 0,
            poisoned: player.poisoned || false
        };
        console.log('playerData updated to:', this.playerData);
        
        // Update prompt based on rank (matching BBC Micro original)
        if (player.rank === 'Wizard') {
            this.promptElement.textContent = '____*';
        } else {
            this.promptElement.textContent = '*';
        }
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
        // Add text to scrolling message log
        const lines = text.split('\n');
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            
            // Special handling for quit sequence dots - append to previous line
            if ((line === '..' || line === '.') && this.messageLog.lastChild) {
                // Append dots to the last text node
                const lastNode = this.messageLog.lastChild;
                if (lastNode.nodeType === Node.TEXT_NODE || lastNode.textContent) {
                    // Find the last text content
                    const walker = document.createTreeWalker(
                        this.messageLog,
                        NodeFilter.SHOW_TEXT,
                        null,
                        false
                    );
                    let lastTextNode = null;
                    while (walker.nextNode()) {
                        lastTextNode = walker.currentNode;
                    }
                    if (lastTextNode) {
                        lastTextNode.textContent += line;
                        continue;
                    }
                }
            }
            
            // Create span for styled text
            const span = document.createElement('span');
            span.className = `msg-${style}`;
            span.textContent = line;
            this.messageLog.appendChild(span);
            
            // Add newline except after last line
            if (i < lines.length - 1) {
                this.messageLog.appendChild(document.createTextNode('\n'));
            }
        }
        
        // Add final newline only if not a dot continuation
        if (text !== '..' && text !== '.') {
            this.messageLog.appendChild(document.createTextNode('\n'));
        }
        
        // Auto-scroll to bottom
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
        
        // Echo command in message log (BBC Micro style - prompt + command scrolls up)
        const promptChar = this.promptElement.textContent;
        this.addMessage(`${promptChar}${command}`, 'normal');
        
        // Send to server
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                command: command
            }));
        }
        
        // Clear input and display
        this.commandInput.value = '';
        this.commandDisplay.textContent = '';
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
            this.commandDisplay.textContent = '';
            return;
        }
        
        this.commandInput.value = this.commandHistory[this.historyIndex];
        this.commandDisplay.textContent = this.commandHistory[this.historyIndex].toUpperCase();
    }
    
    toggleCRTFilter() {
        console.log('Toggling CRT filter from', this.crtFilterEnabled, 'to', !this.crtFilterEnabled);
        this.crtFilterEnabled = !this.crtFilterEnabled;
        localStorage.setItem('crtFilter', this.crtFilterEnabled);
        this.applyCRTFilter();
    }
    
    applyCRTFilter() {
        console.log('Applying CRT filter:', this.crtFilterEnabled);
        if (this.crtFilterEnabled) {
            this.loginScreen.classList.add('crt-filter');
            this.gameScreen.classList.add('crt-filter');
            this.crtToggle.classList.add('active');
        } else {
            this.loginScreen.classList.remove('crt-filter');
            this.gameScreen.classList.remove('crt-filter');
            this.crtToggle.classList.remove('active');
        }
    }
    
    playBeep(count = 1) {
        // Check if sound is enabled
        if (!this.soundEnabled) {
            return;
        }
        
        // Simulate BBC Micro VDU7 beep
        // Characteristics: ~1000Hz square wave, ~100ms duration
        
        // Lazy initialize audio context (requires user interaction)
        if (!this.audioContext) {
            try {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            } catch (e) {
                console.warn('Web Audio API not supported:', e);
                return;
            }
        }
        
        // Play multiple beeps with slight gaps
        for (let i = 0; i < count; i++) {
            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            // BBC Micro beep characteristics
            oscillator.frequency.value = 1000; // Hz - classic BBC Micro frequency
            oscillator.type = 'square'; // Square wave for authentic 8-bit sound
            
            // Volume envelope (quick attack/decay for crisp beep)
            const startTime = this.audioContext.currentTime + (i * 0.15); // 150ms between beeps
            gainNode.gain.setValueAtTime(0.3, startTime); // Moderate volume
            gainNode.gain.exponentialRampToValueAtTime(0.01, startTime + 0.1); // Quick decay
            
            oscillator.start(startTime);
            oscillator.stop(startTime + 0.1); // 100ms duration
        }
    }
    
    toggleSound() {
        console.log('Toggling sound from', this.soundEnabled, 'to', !this.soundEnabled);
        this.soundEnabled = !this.soundEnabled;
        localStorage.setItem('soundEnabled', this.soundEnabled);
        this.applySoundState();
    }
    
    applySoundState() {
        console.log('Applying sound state:', this.soundEnabled);
        if (this.soundEnabled) {
            this.soundToggle.classList.add('active');
            this.soundToggle.querySelector('.button-label').textContent = '🔊';
        } else {
            this.soundToggle.classList.remove('active');
            this.soundToggle.querySelector('.button-label').textContent = '🔇';
        }
    }
    
    showGoing() {
        // Display the GOING farewell screen (matching BBC Micro assembly code)
        // CHR$134 = Yellow, CHR$141 = Double height, CHR$129 = Cyan
        this.loginDisplay.innerHTML = `


<span style="color: #ffff00;">You have just left..</span>

<span class="double-height" style="color: #00ffff;">  CAVE</span>

<span style="color: #ffff00;">(C) 1985 XOB Partners.</span>


<span style="color: #ffffff;">Press any key to start again...</span>`;
        
        this.loginScreen.classList.add('active');
        this.gameScreen.classList.remove('active');
        
        // Wait for any keypress to return to login
        const returnToLogin = (e) => {
            document.removeEventListener('keydown', returnToLogin);
            this.loginState = 'name';
            this.currentInput = '';
            this.playerName = '';
            this.password = '';
            this.updateLoginDisplay();
        };
        document.addEventListener('keydown', returnToLogin);
    }
    
    showLogin() {
        this.loginScreen.classList.add('active');
        this.gameScreen.classList.remove('active');
    }
    
    showGame() {
        // Clear all previous messages
        this.messageLog.textContent = '';
        this.statusMessagesElement.textContent = '';
        this.statusMessages = [];
        
        // Clear command input
        this.commandInput.value = '';
        this.commandDisplay.textContent = '';
        
        // Switch screens
        this.loginScreen.classList.remove('active');
        this.gameScreen.classList.add('active');
        this.commandInput.focus();
    }
}

// Initialize game when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.game = new CaveGame();
});
