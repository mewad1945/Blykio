const express = require('express');
const app = express();
const http = require('http').createServer(app);
const io = require('socket.io')(http, { cors: { origin: "*" } });

app.use(express.static(__dirname));

let rooms = {};

io.on('connection', (socket) => {
    socket.on('createMatch', (data) => {
        const roomId = Math.random().toString(36).substring(2, 6).toUpperCase();
        rooms[roomId] = {
            id: roomId,
            hostId: socket.id,
            hostName: data.name,
            players: [{ id: socket.id, name: data.name }],
            settings: data.settings, // Inkluderar rounds, imposterCount, category
            status: 'lobby',
            word: '',
            imposters: [],
            currentRound: 1,
            turnIndex: 0,
            votes: {}
        };
        socket.join(roomId);
        socket.emit('matchCreated', rooms[roomId]);
    });

    socket.on('getPublicGames', () => {
        const list = Object.values(rooms)
            .filter(r => r.status === 'lobby')
            .map(r => ({
                id: r.id,
                host: r.hostName,
                players: r.players.length,
                max: r.settings.maxPlayers,
                category: r.settings.category,
                rounds: r.settings.rounds
            }));
        socket.emit('publicGamesList', list);
    });

    socket.on('joinMatch', (data) => {
        const room = rooms[data.code];
        if (!room) return socket.emit('error', 'Matchen hittades inte!');
        if (room.players.length >= room.settings.maxPlayers) return socket.emit('error', 'Lobbyn är full!');
        
        room.players.push({ id: socket.id, name: data.name });
        socket.join(data.code);
        socket.emit('matchJoined', room);
        io.to(data.code).emit('updatePlayers', { players: room.players, maxPlayers: room.settings.maxPlayers });
    });

    socket.on('startGame', (roomId) => {
        startNewRound(roomId);
    });

    function startNewRound(roomId) {
        const room = rooms[roomId];
        if (!room) return;

        const wordPool = {
            'Animals': ['Lejon', 'Giraff', 'Haj', 'Panda', 'Krokodil', 'Pingvin', 'Tiger'],
            'Food': ['Pizza', 'Sushi', 'Taco', 'Pasta', 'Kebab', 'Hamburgare', 'Croissant'],
            'Famous People': ['Zlatan', 'Elon Musk', 'Beyonce', 'Messi', 'Trump', 'Ronaldo'],
            'Objects': ['Hammare', 'Klocka', 'Telefon', 'Paraply', 'Kamera', 'Skiftnyckel']
        };
        
        const words = wordPool[room.settings.category] || wordPool['Animals'];
        room.word = words[Math.floor(Math.random() * words.length)];
        
        let shuffled = [...room.players].sort(() => 0.5 - Math.random());
        room.imposters = shuffled.slice(0, room.settings.imposterCount).map(p => p.id);
        
        room.status = 'playing';
        room.turnIndex = 0;
        room.votes = {};

        io.to(roomId).emit('gameStarted', {
            word: room.word,
            imposters: room.imposters,
            turnPlayer: room.players[0].name,
            currentRound: room.currentRound,
            totalRounds: room.settings.rounds
        });
    }

    socket.on('sendWord', (data) => {
        const room = rooms[data.roomId];
        if (!room || room.status !== 'playing') return;

        room.turnIndex++;
        if (room.turnIndex >= room.players.length) {
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

    socket.on('castVote', (data) => {
        const room = rooms[data.roomId];
        if (!room) return;
        room.votes[socket.id] = data.targetId;

        if (Object.keys(room.votes).length === room.players.length) {
            const voteCounts = {};
            Object.values(room.votes).forEach(id => voteCounts[id] = (voteCounts[id] || 0) + 1);
            const votedOutId = Object.keys(voteCounts).reduce((a, b) => voteCounts[a] > voteCounts[b] ? a : b);
            
            const isCorrect = room.imposters.includes(votedOutId);
            const votedOutName = room.players.find(p => p.id === votedOutId).name;

            const isGameOver = room.currentRound >= parseInt(room.settings.rounds);
            
            io.to(data.roomId).emit('roundResult', {
                isCorrect,
                votedOutName,
                imposters: room.players.filter(p => room.imposters.includes(p.id)).map(p => p.name),
                word: room.word,
                isGameOver
            });

            if (!isGameOver) {
                room.currentRound++;
                room.status = 'lobby'; // Väntar på att host ska starta nästa runda
            } else {
                delete rooms[data.roomId]; // Stäng matchen efter sista rundan
            }
        }
    });

    socket.on('disconnect', () => {
        for (const roomId in rooms) {
            if (rooms[roomId].hostId === socket.id) {
                io.to(roomId).emit('leaderLeft');
                delete rooms[roomId];
            }
        }
    });
});

http.listen(3000, () => console.log('Blykio Server: 3000'));
