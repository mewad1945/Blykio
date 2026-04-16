const express = require('express');
const app = express();
const http = require('http').createServer(app);
const io = require('socket.io')(http, { cors: { origin: "*" } });

app.use(express.static(__dirname));

let rooms = {};

io.on('connection', (socket) => {
    // SKAPA MATCH
    socket.on('createMatch', (data) => {
        const roomId = Math.random().toString(36).substring(2, 6).toUpperCase();
        rooms[roomId] = {
            id: roomId,
            hostId: socket.id,
            players: [{ id: socket.id, name: data.name }],
            settings: data.settings,
            status: 'lobby',
            word: '',
            imposters: [],
            turnIndex: 0,
            votes: {} // Sparar vem som röstat på vem
        };
        socket.join(roomId);
        socket.emit('matchCreated', rooms[roomId]);
    });

    // GÅ MED
    socket.on('joinMatch', (data) => {
        const room = rooms[data.code];
        if (!room) return socket.emit('error', 'Matchen hittades inte!');
        room.players.push({ id: socket.id, name: data.name });
        socket.join(data.code);
        socket.emit('matchJoined', room);
        io.to(data.code).emit('updatePlayers', { players: room.players, maxPlayers: room.settings.maxPlayers });
    });

    // STARTA SPELET
    socket.on('startGame', (roomId) => {
        const room = rooms[roomId];
        if (!room) return;

        const wordPool = {
            'Animals': ['Lejon', 'Giraff', 'Panda', 'Haj'],
            'Food': ['Taco', 'Sushi', 'Hamburgare', 'Kebab'],
            'Objects': ['Hammare', 'Dator', 'Klocka', 'Solglasögon']
        };
        const category = room.settings.category;
        const words = wordPool[category] || wordPool['Animals'];
        room.word = words[Math.floor(Math.random() * words.length)];
        
        // Slumpa Imposters baserat på inställning
        let shuffled = [...room.players].sort(() => 0.5 - Math.random());
        room.imposters = shuffled.slice(0, room.settings.imposterCount).map(p => p.id);
        
        room.status = 'playing';
        room.turnIndex = 0;
        room.votes = {};

        io.to(roomId).emit('gameStarted', {
            word: room.word,
            imposters: room.imposters,
            turnPlayer: room.players[0].name
        });
    });

    // HANTERA ORD & RÖSTNINGSFAS
    socket.on('sendWord', (data) => {
        const room = rooms[data.roomId];
        if (!room) return;

        room.turnIndex++;
        
        if (room.turnIndex >= room.players.length) {
            // Alla har pratat -> Gå till röstning
            io.to(data.roomId).emit('startVoting', { players: room.players });
        } else {
            const nextPlayer = room.players[room.turnIndex];
            io.to(data.roomId).emit('newWord', {
                sender: data.name,
                word: data.word,
                nextTurn: nextPlayer.name
            });
        }
    });

    // SAMLA RÖSTER
    socket.on('castVote', (data) => {
        const room = rooms[data.roomId];
        if (!room) return;

        room.votes[socket.id] = data.targetId;

        // Om alla har röstat
        if (Object.keys(room.votes).length === room.players.length) {
            // Räkna vem som fick flest röster
            const voteCounts = {};
            Object.values(room.votes).forEach(id => voteCounts[id] = (voteCounts[id] || 0) + 1);
            const votedOutId = Object.keys(voteCounts).reduce((a, b) => voteCounts[a] > voteCounts[b] ? a : b);
            
            const isCorrect = room.imposters.includes(votedOutId);
            const votedOutName = room.players.find(p => p.id === votedOutId).name;

            io.to(data.roomId).emit('gameResult', {
                isCorrect,
                votedOutName,
                imposters: room.players.filter(p => room.imposters.includes(p.id)).map(p => p.name),
                word: room.word
            });
            room.status = 'lobby';
        }
    });

    // PARTY LEADER DISCONNECT
    socket.on('disconnect', () => {
        for (const roomId in rooms) {
            if (rooms[roomId].hostId === socket.id) {
                io.to(roomId).emit('leaderLeft');
                delete rooms[roomId];
            }
        }
    });
});

http.listen(3000, () => console.log('Blykio rullar!'));
