// Load room data and render map
let roomData = null;
let showWizardDomain = true;
let svg, g;
let zoom, transform;
let currentPlayerRoom = null; // Track player's current room

// Pan and zoom state
let viewBox = { x: 0, y: 0, width: 2000, height: 2000 };
let isDragging = false;
let dragStart = { x: 0, y: 0 };

// Listen for player position updates from game window
window.addEventListener('message', (event) => {
    if (event.data.type === 'player_position') {
        currentPlayerRoom = event.data.room_id;
        console.log('Player moved to room:', currentPlayerRoom);
        highlightPlayerRoom();
    }
});

async function loadRoomData() {
    // Load directly from YAML file
    const response = await fetch('/rooms-parsed.yml');
    const yamlText = await response.text();
    
    // Simple YAML parser for our specific format
    const rooms = {};
    const lines = yamlText.split('\n');
    let currentRoom = null;
    let inExits = false;
    
    for (let line of lines) {
        // Room ID line: "  123:"
        const roomMatch = line.match(/^  (\d+):/);
        if (roomMatch) {
            currentRoom = parseInt(roomMatch[1]);
            rooms[currentRoom] = { id: currentRoom, exits: {} };
            inExits = false;
            continue;
        }
        
        // Name line: "    name: Room Name"
        const nameMatch = line.match(/^    name: (.+)$/);
        if (nameMatch && currentRoom) {
            rooms[currentRoom].name = nameMatch[1];
            continue;
        }
        
        // Exits section start
        if (line.match(/^    exits:/)) {
            inExits = true;
            continue;
        }
        
        // Exit line: "      north: 123"
        const exitMatch = line.match(/^      (\w+): (\d+)$/);
        if (exitMatch && currentRoom && inExits) {
            rooms[currentRoom].exits[exitMatch[1]] = parseInt(exitMatch[2]);
            continue;
        }
        
        // End of exits section
        if (inExits && line.match(/^    \w+:/) && !line.match(/^      /)) {
            inExits = false;
        }
    }
    
    roomData = { rooms };
    initMap();
}

function initMap() {
    svg = document.getElementById('map-svg');
    
    // Create main group for all elements
    g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    svg.appendChild(g);
    
    // Set up pan and zoom
    svg.addEventListener('mousedown', startDrag);
    svg.addEventListener('mousemove', drag);
    svg.addEventListener('mouseup', endDrag);
    svg.addEventListener('mouseleave', endDrag);
    svg.addEventListener('wheel', handleZoom);
    
    renderMap();
}

function startDrag(e) {
    isDragging = true;
    dragStart = { x: e.clientX, y: e.clientY };
}

function drag(e) {
    if (!isDragging) return;
    
    const dx = e.clientX - dragStart.x;
    const dy = e.clientY - dragStart.y;
    
    viewBox.x -= dx * (viewBox.width / svg.clientWidth);
    viewBox.y -= dy * (viewBox.height / svg.clientHeight);
    
    updateViewBox();
    
    dragStart = { x: e.clientX, y: e.clientY };
}

function endDrag() {
    isDragging = false;
}

function handleZoom(e) {
    e.preventDefault();
    
    const zoomFactor = e.deltaY > 0 ? 1.1 : 0.9;
    const mouseX = e.clientX;
    const mouseY = e.clientY;
    
    // Calculate mouse position in SVG coordinates
    const svgX = viewBox.x + (mouseX / svg.clientWidth) * viewBox.width;
    const svgY = viewBox.y + (mouseY / svg.clientHeight) * viewBox.height;
    
    // Zoom
    viewBox.width *= zoomFactor;
    viewBox.height *= zoomFactor;
    
    // Adjust position to zoom towards mouse
    viewBox.x = svgX - (mouseX / svg.clientWidth) * viewBox.width;
    viewBox.y = svgY - (mouseY / svg.clientHeight) * viewBox.height;
    
    updateViewBox();
}

function updateViewBox() {
    svg.setAttribute('viewBox', `${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`);
}

function renderMap() {
    // Clear existing content
    g.innerHTML = '';
    
    // Filter rooms based on wizard domain toggle
    const rooms = showWizardDomain ? 
        roomData.rooms : 
        Object.fromEntries(Object.entries(roomData.rooms).filter(([id]) => {
            const roomId = parseInt(id);
            return roomId < 16 || roomId > 20;
        }));
    
    // Calculate positions using force-directed layout
    const positions = calculatePositions(rooms);
    
    // Draw connections first (so they're behind nodes)
    drawConnections(rooms, positions);
    
    // Draw rooms
    drawRooms(rooms, positions);
    
    updateViewBox();
}

function calculatePositions(rooms) {
    const positions = {};
    const roomIds = Object.keys(rooms).map(id => parseInt(id));
    
    // Balanced grid spacing - not too spread out, not too tight
    const gridSize = 70;
    
    // Direction vectors for traditional dungeon map layout
    const directions = {
        'north': { dx: 0, dy: -1 },
        'south': { dx: 0, dy: 1 },
        'east': { dx: 1, dy: 0 },
        'west': { dx: -1, dy: 0 },
        'northeast': { dx: 1, dy: -1 },
        'northwest': { dx: -1, dy: -1 },
        'southeast': { dx: 1, dy: 1 },
        'southwest': { dx: -1, dy: 1 },
        // UP/DOWN will be handled with visual indicators
        'up': { dx: 0, dy: 0 },
        'down': { dx: 0, dy: 0 }
    };
    
    const placed = new Set();
    
    // Function to place a connected component starting from a room
    function placeComponent(startId, startX, startY) {
        const queue = [{ id: startId, x: startX, y: startY }];
        positions[startId] = { x: startX, y: startY };
        placed.add(startId);
        
        while (queue.length > 0) {
            const current = queue.shift();
            const room = rooms[current.id];
            const exits = room.exits || {};
            
            // Process each exit
            for (const [direction, targetId] of Object.entries(exits)) {
                if (!rooms[targetId] || placed.has(targetId)) continue;
                
                const dir = directions[direction.toLowerCase()];
                if (!dir) continue;
                
                // Calculate position based on direction
                let newX = current.x + dir.dx * gridSize;
                let newY = current.y + dir.dy * gridSize;
                
                // Handle UP/DOWN - offset slightly to show they're on different levels
                if (direction.toLowerCase() === 'up') {
                    newX = current.x + gridSize * 0.3;
                    newY = current.y - gridSize * 0.3;
                } else if (direction.toLowerCase() === 'down') {
                    newX = current.x - gridSize * 0.3;
                    newY = current.y + gridSize * 0.3;
                }
                
                // Check if position is already occupied (with tighter tolerance)
                let occupied = false;
                for (const [placedId, pos] of Object.entries(positions)) {
                    if (Math.abs(pos.x - newX) < gridSize * 0.4 && 
                        Math.abs(pos.y - newY) < gridSize * 0.4) {
                        occupied = true;
                        break;
                    }
                }
                
                // If occupied, try to find nearby free spot (smaller search radius)
                if (occupied) {
                    let found = false;
                    for (let offsetX = -1; offsetX <= 1 && !found; offsetX++) {
                        for (let offsetY = -1; offsetY <= 1 && !found; offsetY++) {
                            if (offsetX === 0 && offsetY === 0) continue;
                            
                            const testX = newX + offsetX * gridSize * 0.4;
                            const testY = newY + offsetY * gridSize * 0.4;
                            
                            let testOccupied = false;
                            for (const pos of Object.values(positions)) {
                                if (Math.abs(pos.x - testX) < gridSize * 0.4 && 
                                    Math.abs(pos.y - testY) < gridSize * 0.4) {
                                    testOccupied = true;
                                    break;
                                }
                            }
                            
                            if (!testOccupied) {
                                newX = testX;
                                newY = testY;
                                found = true;
                            }
                        }
                    }
                }
                
                positions[targetId] = { x: newX, y: newY };
                placed.add(targetId);
                queue.push({ id: targetId, x: newX, y: newY });
            }
        }
    }
    
    // Place main cave starting from room 1
    placeComponent(1, 0, 0);
    
    // Find bounds of main cave to position wizard domain nearby
    let mainMinX = Infinity, mainMaxX = -Infinity;
    let mainMinY = Infinity, mainMaxY = -Infinity;
    
    for (const [id, pos] of Object.entries(positions)) {
        const roomId = parseInt(id);
        if (roomId >= 16 && roomId <= 20) continue;
        mainMinX = Math.min(mainMinX, pos.x);
        mainMaxX = Math.max(mainMaxX, pos.x);
        mainMinY = Math.min(mainMinY, pos.y);
        mainMaxY = Math.max(mainMaxY, pos.y);
    }
    
    // Place wizard domain to the right of main cave with more spacing
    const wizardStartX = mainMaxX + gridSize * 5;
    const wizardStartY = (mainMinY + mainMaxY) / 2;
    
    if (!placed.has(16)) {
        placeComponent(16, wizardStartX, wizardStartY);
    }
    
    // Place any remaining unconnected rooms near the main cluster
    roomIds.forEach(id => {
        if (!placed.has(id)) {
            // Place isolated rooms with more spacing
            positions[id] = {
                x: mainMaxX + gridSize * 4,
                y: mainMinY + (id % 10) * gridSize
            };
            placed.add(id);
        }
    });
    
    // Center the entire map
    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;
    
    for (const pos of Object.values(positions)) {
        minX = Math.min(minX, pos.x);
        maxX = Math.max(maxX, pos.x);
        minY = Math.min(minY, pos.y);
        maxY = Math.max(maxY, pos.y);
    }
    
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;
    const offsetX = 1000 - centerX;
    const offsetY = 1000 - centerY;
    
    // Apply centering offset to all rooms
    for (const id in positions) {
        positions[id].x += offsetX;
        positions[id].y += offsetY;
    }
    
    return positions;
}

function drawConnections(rooms, positions) {
    Object.entries(rooms).forEach(([id, room]) => {
        const roomId = parseInt(id);
        const exits = room.exits || {};
        const isWizard = roomId >= 16 && roomId <= 20;
        
        Object.entries(exits).forEach(([direction, targetId]) => {
            if (!positions[targetId]) return;
            
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', positions[roomId].x);
            line.setAttribute('y1', positions[roomId].y);
            line.setAttribute('x2', positions[targetId].x);
            line.setAttribute('y2', positions[targetId].y);
            
            // Style UP/DOWN connections differently
            const isVertical = direction.toLowerCase() === 'up' || direction.toLowerCase() === 'down';
            if (isVertical) {
                line.setAttribute('class', `connection-line ${isWizard ? 'wizard' : ''}`);
                line.setAttribute('stroke-dasharray', '5,5');
                line.setAttribute('stroke-opacity', '0.5');
            } else {
                line.setAttribute('class', `connection-line ${isWizard ? 'wizard' : ''}`);
            }
            
            g.appendChild(line);
        });
    });
}

function drawRooms(rooms, positions) {
    Object.entries(rooms).forEach(([id, room]) => {
        const roomId = parseInt(id);
        const pos = positions[roomId];
        const isWizard = roomId >= 16 && roomId <= 20;
        const isEntrance = roomId === 1;
        
        // Create group for room
        const roomGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        roomGroup.setAttribute('class', 'room-node');
        roomGroup.setAttribute('data-room-id', roomId);
        
        // Square instead of circle (BBC Micro style)
        const size = 24;
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', pos.x - size/2);
        rect.setAttribute('y', pos.y - size/2);
        rect.setAttribute('width', size);
        rect.setAttribute('height', size);
        rect.setAttribute('class', `room-circle ${isWizard ? 'wizard' : ''} ${isEntrance ? 'entrance' : ''}`);
        
        // Text
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', pos.x);
        text.setAttribute('y', pos.y);
        text.setAttribute('class', 'room-text');
        text.textContent = roomId;
        
        roomGroup.appendChild(rect);
        roomGroup.appendChild(text);
        
        // Add click handler
        roomGroup.addEventListener('click', () => showRoomInfo(roomId, room));
        roomGroup.addEventListener('mouseenter', () => showRoomInfo(roomId, room));
        
        g.appendChild(roomGroup);
    });
}

function showRoomInfo(roomId, room) {
    const info = document.getElementById('info');
    const content = document.getElementById('info-content');
    
    const exits = room.exits || {};
    const exitList = Object.entries(exits)
        .map(([dir, target]) => `${dir}: ${target}`)
        .join('<br>');
    
    content.innerHTML = `
        <strong>Room ${roomId}</strong><br>
        ${room.name || 'Unnamed'}<br>
        <br>
        <strong>Exits:</strong><br>
        ${exitList || 'None'}
    `;
    
    info.style.display = 'block';
}

function resetView() {
    viewBox = { x: 0, y: 0, width: 2000, height: 2000 };
    updateViewBox();
}

function toggleWizard() {
    showWizardDomain = !showWizardDomain;
    renderMap();
}

function highlightPlayerRoom() {
    if (!currentPlayerRoom) return;
    
    // Remove previous highlight
    const previousHighlight = document.querySelector('.room-circle.player-here');
    if (previousHighlight) {
        previousHighlight.classList.remove('player-here');
    }
    
    // Add highlight to current room
    const roomNode = document.querySelector(`[data-room-id="${currentPlayerRoom}"]`);
    if (roomNode) {
        const rect = roomNode.querySelector('.room-circle');
        if (rect) {
            rect.classList.add('player-here');
        }
    }
}

// Load data on page load
loadRoomData();
