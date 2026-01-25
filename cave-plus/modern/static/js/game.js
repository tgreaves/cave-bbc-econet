// Cave-Plus Web Client v1.6 - Auto-scroll after disk activity
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
        this.loginInputEnabled = true; // Flag to disable login input temporarily
        
        // CRT filter state (load from localStorage, default to ON)
        const savedFilter = localStorage.getItem('crtFilter');
        this.crtFilterEnabled = savedFilter === null ? true : savedFilter === 'true';
        
        // Sound state (load from localStorage, default to ON)
        const savedSound = localStorage.getItem('soundEnabled');
        this.soundEnabled = savedSound === null ? true : savedSound === 'true';
        
        // Audio context for BBC Micro beep simulation
        this.audioContext = null;
        
        // Preloaded audio buffers for disk sounds
        this.audioBuffers = {
            seek: null,
            step: null
        };
        
        // Disk activity state - queue messages during disk operations
        this.diskActivityInProgress = false;
        this.messageQueue = [];
        
        this.initElements();
        this.initEventListeners();
        this.applyCRTFilter();
        this.applySoundState();
        // Note: preloadSounds() is called on first keypress (user interaction required)
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
        // Initialize AudioContext on first keypress (user interaction)
        if (!this.audioContext) {
            try {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                console.log('🔊 AudioContext initialized on first keypress');
                // Resume if suspended
                if (this.audioContext.state === 'suspended') {
                    this.audioContext.resume();
                }
                // Now preload sounds with the active context
                this.preloadSounds();
            } catch (e) {
                console.error('Failed to initialize AudioContext:', e);
            }
        }
        
        // Check if login input is enabled
        if (!this.loginInputEnabled) {
            return;
        }
        
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
<span style="color: #ffffff;">Modern (C) Tristan Greaves 2026</span>


<span style="color: #ffffff;">Please enter your name : ${this.currentInput}<span class="cursor">_</span></span>`;
        } else if (this.loginState === 'password') {
            // Password is NOT shown (VDU21 disabled output in original)
            this.loginDisplay.innerHTML = `<span class="double-height" style="color: #ffff00;">CAVE-PLUS</span><span style="color: #ffffff;">(C) XOB 1988 </span><span class="double-height" style="color: #ffffff;">Version 1.00</span>

<span class="double-height" style="color: #ffff00;">From CAVE</span><span style="color: #ffffff;">(C) GJL WOTWECP 1985</span>
<span style="color: #ffffff;">Modern (C) Tristan Greaves 2026</span>


<span style="color: #ffffff;">Please enter your name : ${this.playerName}</span>

<span style="color: #ffffff;">Enter your password ${this.playerName} : <span class="cursor">_</span></span>`;
        }
    }
    
    showLoginError(message) {
        this.loginDisplay.innerHTML = `<span class="double-height" style="color: #ffff00;">CAVE-PLUS</span><span style="color: #ffffff;">(C) XOB 1988 </span><span class="double-height" style="color: #ffffff;">Version 1.00</span>

<span class="double-height" style="color: #ffff00;">From CAVE</span><span style="color: #ffffff;">(C) GJL WOTWECP 1985</span>
<span style="color: #ffffff;">Modern (C) Tristan Greaves 2026</span>


<span style="color: #ffffff;">Please enter your name : ${this.playerName}</span>

<span style="color: #ffffff;">Enter your password ${this.playerName} : </span>

<span style="color: #ffffff;">${message}</span>

<span style="color: #ffffff;">Enter your password ${this.playerName} : <span class="cursor">_</span></span>`;
        this.currentInput = '';
    }
    
    connect() {
        // Disable login input during connection
        this.loginInputEnabled = false;
        
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
    
    async handleMessage(data) {
        // If disk activity is in progress and this isn't a disk_activity message, queue it
        if (this.diskActivityInProgress && data.type !== 'disk_activity') {
            console.log('🖴 Queuing message during disk activity:', data.type);
            this.messageQueue.push(data);
            return;
        }
        
        switch (data.type) {
            case 'disk_activity':
                // Play disk sounds and block until complete
                console.log('🖴 Disk activity started:', data.operation);
                this.diskActivityInProgress = true;
                
                // Hide prompt during disk activity
                this.promptElement.style.display = 'none';
                this.commandDisplay.style.display = 'none';
                const cursorDisk = this.messageLog.querySelector('.cursor');
                if (cursorDisk) cursorDisk.style.display = 'none';
                
                const operation = data.operation || 'read';
                await this.playDiskOperation(operation);
                this.diskActivityInProgress = false;
                console.log('🖴 Disk activity complete, processing', this.messageQueue.length, 'queued messages');
                
                // Process any queued messages
                while (this.messageQueue.length > 0) {
                    const queuedMessage = this.messageQueue.shift();
                    await this.handleMessage(queuedMessage);
                }
                
                // Show prompt after all queued messages are processed
                // BUT only if input hasn't been disabled (e.g., during QUIT/death)
                console.log('🖴 Disk activity done. Input disabled?', this.commandInput.disabled);
                if (!this.commandInput.disabled) {
                    console.log('   Re-showing prompt');
                    this.promptElement.style.display = 'inline';
                    this.commandDisplay.style.display = 'inline';
                    if (cursorDisk) cursorDisk.style.display = 'inline';
                } else {
                    console.log('   Keeping prompt hidden (input disabled)');
                }
                
                // Scroll to show the prompt
                this.messageLog.scrollTop = this.messageLog.scrollHeight;
                break;
            
            case 'disable_input':
                // Disable command input (used during QUIT/death sequence)
                this.commandInput.disabled = true;
                this.commandInput.style.opacity = '0.5';
                // Hide the prompt line
                this.promptElement.style.display = 'none';
                this.commandDisplay.style.display = 'none';
                const cursor = this.messageLog.querySelector('.cursor');
                if (cursor) cursor.style.display = 'none';
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
<span style="color: #ffffff;">Modern (C) Tristan Greaves 2026</span>


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
                        this.loginInputEnabled = true;  // Re-enable input
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
                
                // Check if there's a separate status message (for commands like BURN, SHOOT, STAB)
                if (data.status_message) {
                    // Main message goes to main window
                    this.addMessage(text, style);
                    // Status message goes to status bar
                    this.addStatusMessage(data.status_message);
                } else if (style === 'combat' || style === 'death' || style === 'action') {
                    // Combat and important messages go to status area
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
        
        // Display room text (scrolls up)
        this.addMessage(desc, 'normal');
        
        // BBC Micro behavior: Display graphic as overlay on top of scrolled text
        const graphicsOverlay = document.getElementById('graphics-overlay');
        const roomGraphic = document.getElementById('room-graphic');
        
        if (room.has_graphic && room.graphic_url) {
            // Hide overlay first to prevent old image from flashing
            graphicsOverlay.style.display = 'none';
            
            // Load new image and show when ready
            roomGraphic.onload = () => {
                graphicsOverlay.style.display = 'block';
            };
            roomGraphic.src = room.graphic_url;
        } else {
            graphicsOverlay.style.display = 'none';
        }
        
        // Scroll to bottom to show prompt
        this.messageLog.scrollTop = this.messageLog.scrollHeight;
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
        // Get the prompt elements (they're at the end of messageLog)
        const promptSpan = document.getElementById('prompt');
        const commandDisplay = document.getElementById('command-display');
        const cursor = this.messageLog.querySelector('.cursor');
        
        // On first message, add padding to push content to bottom (BBC Micro style)
        if (!this.messageLog.querySelector('.top-spacer')) {
            const spacer = document.createElement('div');
            spacer.className = 'top-spacer';
            spacer.style.height = '100%'; // Will be reduced as content is added
            this.messageLog.insertBefore(spacer, this.messageLog.firstChild);
        }
        
        // Add text to scrolling message log (before the prompt)
        const lines = text.split('\n');
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            
            // Special handling for quit sequence dots - append to previous line
            if ((line === '..' || line === '.') && this.messageLog.childNodes.length > 3) {
                // Find the last text node before the prompt
                const walker = document.createTreeWalker(
                    this.messageLog,
                    NodeFilter.SHOW_TEXT,
                    null,
                    false
                );
                let lastTextNode = null;
                let node;
                while ((node = walker.nextNode())) {
                    // Stop before the prompt elements
                    if (node.parentNode === this.messageLog && 
                        (node.nextSibling === promptSpan || node.nextSibling === commandDisplay)) {
                        break;
                    }
                    lastTextNode = node;
                }
                if (lastTextNode) {
                    lastTextNode.textContent += line;
                    continue;
                }
            }
            
            // Create span for styled text
            const span = document.createElement('span');
            span.className = `msg-${style}`;
            
            // Check if line contains HTML color markup (from Teletext colors)
            if (line.includes('<span class="teletext-')) {
                // Use innerHTML for colored text
                span.innerHTML = line;
            } else {
                // Use textContent for plain text (safer)
                span.textContent = line;
            }
            
            // Insert before the prompt
            this.messageLog.insertBefore(span, promptSpan);
            
            // Add newline except after last line
            if (i < lines.length - 1) {
                this.messageLog.insertBefore(document.createTextNode('\n'), promptSpan);
            }
        }
        
        // Add final newline only if not a dot continuation
        if (text !== '..' && text !== '.') {
            this.messageLog.insertBefore(document.createTextNode('\n'), promptSpan);
        }
        
        // Adjust spacer height to keep content at bottom until it fills the screen
        const spacer = this.messageLog.querySelector('.top-spacer');
        if (spacer) {
            const logHeight = this.messageLog.clientHeight;
            const contentHeight = this.messageLog.scrollHeight - spacer.offsetHeight;
            
            if (contentHeight < logHeight) {
                // Content doesn't fill screen yet, adjust spacer
                spacer.style.height = (logHeight - contentHeight) + 'px';
            } else {
                // Content fills screen, remove spacer
                spacer.remove();
            }
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
    
    async playDiskOperation(type = 'read') {
        // Play complete disk operation using real BBC Micro disk sounds
        // Returns a promise that resolves when sound completes
        if (!this.soundEnabled) {
            // Still add delay even if sound is off (authentic disk timing)
            return new Promise(resolve => {
                setTimeout(resolve, type === 'read' ? 400 : 600);
            });
        }
        
        console.log('🖴 Playing disk operation:', type);
        
        return new Promise(async (resolve) => {
            // Play seek.wav first
            await this.playWavFile('/static/sounds/seek.wav');
            
            // Small delay between seek and steps
            await new Promise(r => setTimeout(r, 100));
            
            // Play step.wav 2-3 times
            const steps = 2 + Math.floor(Math.random() * 2); // 2-3 steps
            console.log('   Playing', steps, 'steps');
            for (let i = 0; i < steps; i++) {
                await this.playWavFile('/static/sounds/step.wav');
                if (i < steps - 1) {
                    await new Promise(r => setTimeout(r, 50)); // 50ms between steps
                }
            }
            
            // Resolve after operation completes
            setTimeout(resolve, type === 'read' ? 200 : 400);
        });
    }
    
    async playWavFile(url) {
        // Play a WAV file using Web Audio API
        if (!this.soundEnabled) {
            return;
        }
        
        // Lazy initialize audio context
        if (!this.audioContext) {
            try {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                console.log('   Audio context created:', this.audioContext.state);
            } catch (e) {
                console.error('   Failed to create audio context:', e);
                return;
            }
        }
        
        // Resume audio context if suspended (browser autoplay policy)
        if (this.audioContext.state === 'suspended') {
            await this.audioContext.resume();
        }
        
        try {
            let audioBuffer;
            
            // Check if we have a preloaded buffer for this sound
            if (url === '/static/sounds/seek.wav' && this.audioBuffers.seek) {
                audioBuffer = this.audioBuffers.seek;
                console.log('   Using cached seek.wav');
            } else if (url === '/static/sounds/step.wav' && this.audioBuffers.step) {
                audioBuffer = this.audioBuffers.step;
                console.log('   Using cached step.wav');
            } else {
                // Fetch and decode the audio file
                console.log('   Fetching audio file:', url);
                const response = await fetch(url);
                const arrayBuffer = await response.arrayBuffer();
                audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
            }
            
            // Create and play the sound
            const source = this.audioContext.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(this.audioContext.destination);
            
            // Return a promise that resolves when the sound finishes
            return new Promise((resolve) => {
                source.onended = resolve;
                source.start(0);
            });
        } catch (e) {
            console.error('   Error playing WAV file:', url, e);
        }
    }
    
    async preloadSounds() {
        // Preload disk sound effects for instant playback
        console.log('🔊 Preloading disk sound effects...');
        
        try {
            // Initialize audio context
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }
            
            // Preload seek.wav
            const seekResponse = await fetch('/static/sounds/seek.wav');
            const seekBuffer = await seekResponse.arrayBuffer();
            this.audioBuffers.seek = await this.audioContext.decodeAudioData(seekBuffer);
            console.log('   ✅ Preloaded seek.wav');
            
            // Preload step.wav
            const stepResponse = await fetch('/static/sounds/step.wav');
            const stepBuffer = await stepResponse.arrayBuffer();
            this.audioBuffers.step = await this.audioContext.decodeAudioData(stepBuffer);
            console.log('   ✅ Preloaded step.wav');
            
            console.log('🔊 All disk sounds preloaded successfully!');
        } catch (e) {
            console.error('⚠️  Failed to preload sounds:', e);
            // Non-fatal - sounds will be loaded on-demand if preload fails
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
        
        // Disable login input handler while on GOING screen
        this.loginInputEnabled = false;
        
        // Wait for any keypress to return to login
        const returnToLogin = (e) => {
            // Prevent this key from being processed by login handler
            e.preventDefault();
            e.stopPropagation();
            document.removeEventListener('keydown', returnToLogin);
            
            // Reset login state
            this.loginState = 'name';
            this.currentInput = '';
            this.playerName = '';
            this.password = '';
            
            // Re-enable login input handler
            this.loginInputEnabled = true;
            
            // Update display to show name entry screen
            this.updateLoginDisplay();
        };
        document.addEventListener('keydown', returnToLogin);
    }
    
    showLogin() {
        this.loginScreen.classList.add('active');
        this.gameScreen.classList.remove('active');
    }
    
    showGame() {
        // Clear all previous messages but keep the prompt
        // Remove all child nodes except the last 3 (prompt, command-display, cursor)
        while (this.messageLog.childNodes.length > 3) {
            this.messageLog.removeChild(this.messageLog.firstChild);
        }
        
        this.statusMessagesElement.textContent = '';
        this.statusMessages = [];
        
        // Clear command input and re-enable it
        this.commandInput.value = '';
        this.commandInput.disabled = false;
        this.commandInput.style.opacity = '1';
        this.commandDisplay.textContent = '';
        
        // Show the prompt elements (in case they were hidden)
        this.promptElement.style.display = 'inline';
        this.commandDisplay.style.display = 'inline';
        const cursor = this.messageLog.querySelector('.cursor');
        if (cursor) cursor.style.display = 'inline';
        
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
