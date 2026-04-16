const express = require('express');
const app = express();
const http = require('http').createServer(app);
const io = require('socket.io')(http, {
    cors: { origin: "*", methods: ["GET", "POST"] }
});
const path = require('path');

app.use(express.static(__dirname));

// Rum-data
const rooms = {};

// Hjälpfunktion: Skapa slumpmässig kod (t.ex. AX42)
function generateRoomId() {
    return Math.random().toString(36).substring(2, 6).toUpperCase();
}

io.on('connection', (socket) => {
    console.log('Spelare ansluten:', socket.id);

    // 1. Skapa match
    socket.on('createMatch', (data) => {
        const roomId = generateRoomId();
        rooms[roomId] = {
            id: roomId,
            host: data.name,
            players: [{ id: socket.id, name: data.name }],
            settings: data.settings,
            status: 'lobby', // lobby, playing, voting
            word: '',
            imposters: [],
            turnIndex: 0
        };
        socket.join(roomId);
        socket.emit('matchCreated', rooms[roomId]);
    });

    // 2. Hämta publika spel
    socket.on('getPublicGames', () => {
        const publicGames = Object.values(rooms)
            .filter(r => r.settings.isPublic && r.status === 'lobby')
            .map(r => ({
                id: r.id,
                host: r.host,
                players: r.players.length,
                max: r.settings.maxPlayers,
                category: r.settings.category
            }));
        socket.emit('publicGamesList', publicGames);
    });

    // 3. Gå med i match
    socket.on('joinMatch', (data) => {
        const room = rooms[data.code];
        if (!room) return socket.emit('error', 'Matchen hittades inte!');
        if (room.players.length >= room.settings.maxPlayers) return socket.emit('error', 'Lobbyn är full!');
        
        room.players.push({ id: socket.id, name: data.name });
        socket.join(data.code);
        
        // Säg till den som joinar
        socket.emit('matchJoined', room);
        
        // Uppdatera alla i rummet
        io.to(data.code).emit('updatePlayers', {
            players: room.players,
            maxPlayers: room.settings.maxPlayers
        });
    });

    // 4. Starta spelet
    socket.on('startGame', (roomId) => {
        const room = rooms[roomId];
        if (!room) return;

        room.status = 'playing';
        
        // Välj ett ord (Här kan du bygga ut med riktiga ordlistor per kategori)
        const words = {
            'Animals': ['Lejon', 'Hund', 'Giraff', 'Elefant'],
            'Food': ['Pizza', 'Pasta', 'Sushi', 'Taco'],
            'Famous People': ['Zlatan', 'Einstein', 'Elon Musk'],
            'Objects': ['Hammare', 'Telefon', 'Klocka']
        };
        const catWords = words[room.settings.category] || words['Animals'];
        room.word = catWords[Math.floor(Math.random() * catWords.length)];

        // Välj Imposter
        const randomPlayer = room.players[Math.floor(Math.random() * room.players.length)];
        room.imposters = [randomPlayer.id];

        io.to(roomId).emit('gameStarted', {
            word: room.word,
            imposters: room.imposters,
            turnPlayer: room.players[0].name
        });
    });

    // 5. Hantera ord-skickande
    socket.on('sendWord', (data) => {
        const room = rooms[data.roomId];
        if (!room) return;

        room.turnIndex++;
        
        const isVoteTime = room.turnIndex >= room.players.length;
        const nextPlayer = room.players[room.turnIndex % room.players.length];

        io.to(data.roomId).emit('newWord', {
            sender: data.name,
            word: data.word,
            isVoteTime: isVoteTime,
            nextTurn: nextPlayer ? nextPlayer.name : null,
            allPlayers: room.players
        });
    });

    // 6. Koppla ifrån
    socket.on('disconnect', () => {
        // Här kan man lägga till logik för att ta bort spelaren ur rummet
        console.log('Spelare lämnade');
    });
});

const PORT = 3000;
http.listen(PORT, () => {
    console.log(`Blykio Server rullar på port ${PORT}`);
});
