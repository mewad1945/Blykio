const express = require('express');
const app = express();
const http = require('http').createServer(app);
const io = require('socket.io')(http, { cors: { origin: "*" } });

app.use(express.static(__dirname));

let rooms = {};

const wordPools = {
    'sv': {
        'Djur 🦁': ['Lejon', 'Giraff', 'Haj', 'Panda', 'Krokodil', 'Pingvin', 'Tiger', 'Elefant', 'Uggla', 'Varg', 'Häst', 'Katt', 'Hund', 'Apa', 'Älg', 'Björn', 'Räv', 'Säl', 'Gepard', 'Flodhäst', 'Zebra', 'Orm', 'Örn', 'Sköldpadda', 'Hamster'],
        'Mat 🍕': ['Pizza', 'Sushi', 'Taco', 'Pasta', 'Kebab', 'Hamburgare', 'Sallad', 'Soppa', 'Pannkakor', 'Stek', 'Lasagne', 'Smörgås', 'Gröt', 'Wok', 'Paella', 'Risotto', 'Glass', 'Tårta', 'Bulle', 'Paj', 'Falafel', 'Nudlar', 'Omelett', 'Curry', 'Dumplings'],
        'Kändisar ⭐': ['Zlatan', 'Elon Musk', 'Beyonce', 'Messi', 'Trump', 'Ronaldo', 'Zara Larsson', 'Avicii', 'Rihanna', 'Drake', 'Bill Gates', 'Taylor Swift', 'Brad Pitt', 'Kim Kardashian', 'LeBron James', 'Ariana Grande', 'Eminem', 'Will Smith', 'Tom Cruise', 'Lady Gaga', 'PewDiePie', 'Greta Thunberg', 'Mark Zuckerberg', 'Oprah', 'Justin Bieber'],
        'Platser 🌍': ['Paris', 'London', 'New York', 'Tokyo', 'Stockholm', 'Rom', 'Berlin', 'Dubai', 'Sydney', 'Kina', 'Egypten', 'Island', 'Spanien', 'Brasilien', 'Indien', 'Skogen', 'Stranden', 'Öknen', 'Gymmet', 'Skolan', 'Sjukhuset', 'Flygplatsen', 'Månen', 'Mars', 'Hollywood'],
        'Föremål 📦': ['Klocka', 'Telefon', 'Kamera', 'Dator', 'Hammare', 'Paraply', 'Nycklar', 'Plånbok', 'Spegel', 'Tandborste', 'Lampa', 'Stol', 'Bok', 'Cykel', 'Gitarr', 'Kudde', 'Glasögon', 'Skor', 'Väska', 'Tidning', 'Fjärrkontroll', 'Kniv', 'Kompass', 'Tändstickor', 'Batteri']
    },
    'en': {
        'Animals 🦁': ['Lion', 'Giraffe', 'Shark', 'Panda', 'Crocodile', 'Penguin', 'Tiger', 'Elephant', 'Owl', 'Wolf', 'Horse', 'Cat', 'Dog', 'Monkey', 'Moose', 'Bear', 'Fox', 'Seal', 'Cheetah', 'Hippo', 'Zebra', 'Snake', 'Eagle', 'Turtle', 'Hamster'],
        'Food 🍕': ['Pizza', 'Sushi', 'Taco', 'Pasta', 'Kebab', 'Burger', 'Salad', 'Soup', 'Pancakes', 'Steak', 'Lasagna', 'Sandwich', 'Porridge', 'Wok', 'Paella', 'Risotto', 'Ice Cream', 'Cake', 'Bun', 'Pie', 'Falafel', 'Noodles', 'Omelette', 'Curry', 'Dumplings'],
        'Famous People ⭐': ['Zlatan', 'Elon Musk', 'Beyonce', 'Messi', 'Trump', 'Ronaldo', 'Zara Larsson', 'Avicii', 'Rihanna', 'Drake', 'Bill Gates', 'Taylor Swift', 'Brad Pitt', 'Kim Kardashian', 'LeBron James', 'Ariana Grande', 'Eminem', 'Will Smith', 'Tom Cruise', 'Lady Gaga', 'PewDiePie', 'Greta Thunberg', 'Mark Zuckerberg', 'Oprah', 'Justin Bieber'],
        'Places 🌍': ['Paris', 'London', 'New York', 'Tokyo', 'Stockholm', 'Rome', 'Berlin', 'Dubai', 'Sydney', 'China', 'Egypt', 'Iceland', 'Spain', 'Brazil', 'India', 'The Forest', 'The Beach', 'Desert', 'Gym', 'School', 'Hospital', 'Airport', 'The Moon', 'Mars', 'Hollywood'],
        'Objects 📦': ['Watch', 'Phone', 'Camera', 'Computer', 'Hammer', 'Umbrella', 'Keys', 'Wallet', 'Mirror', 'Toothbrush', 'Lamp', 'Chair', 'Book', 'Bicycle', 'Guitar', 'Pillow', 'Glasses', 'Shoes', 'Bag', 'Magazine', 'Remote', 'Knife', 'Compass', 'Matches', 'Battery']
    }
};

io.on('connection', (socket) => {
    socket.on('createMatch', (data) => {
        const roomId = Math.random().toString(36).substring(2, 6).toUpperCase();
        rooms[roomId] = {
            id: roomId, hostId: socket.id, hostName: data.name,
            players: [{ id: socket.id, name: data.name }],
            settings: data.settings, status: 'lobby', word: '', imposters: [], totalMessagesSent: 0, votes: {}
        };
        socket.join(roomId);
        socket.emit('matchCreated', rooms[roomId]);
    });

    socket.on('getPublicGames', () => {
        const list = Object.values(rooms)
            .filter(r => r.status === 'lobby' && r.settings.isPublic)
            .map(r => ({
                id: r.id, host: r.hostName, players: r.players.length,
                max: r.settings.maxPlayers, category: r.settings.category
            }));
        socket.emit('publicGamesList', list);
    });

    socket.on('joinMatch', (data) => {
        const room = rooms[data.code];
        if (!room) return socket.emit('error', 'Match hittades inte!');
        if (room.players.length >= room.settings.maxPlayers) return socket.emit('error', 'Lobbyn är full!');
        
        room.players.push({ id: socket.id, name: data.name });
        socket.join(data.code);
        socket.emit('matchJoined', room);
        io.to(data.code).emit('updatePlayers', { players: room.players });
    });

    socket.on('startGame', (roomId) => {
        const room = rooms[roomId];
        if (!room) return;
        const lang = room.settings.language || 'sv';
        const pool = wordPools[lang][room.settings.category];
        room.word = pool[Math.floor(Math.random() * pool.length)];
        let shuffled = [...room.players].sort(() => 0.5 - Math.random());
        room.imposters = shuffled.slice(0, parseInt(room.settings.imposterCount)).map(p => p.id);
        room.status = 'playing';
        io.to(roomId).emit('preparingGame', { imposters: room.imposters, word: room.word });
    });

    socket.on('gameReady', (roomId) => {
        const room = rooms[roomId];
        if(room) {
            io.to(roomId).emit('gameStarted', {
                word: room.word, imposters: room.imposters,
                turnPlayer: room.players[0].name, turnsPerPlayer: room.settings.turnsPerPlayer
            });
        }
    });

    socket.on('sendWord', (data) => {
        const room = rooms[data.roomId];
        if (!room || room.status !== 'playing') return;
        room.totalMessagesSent++;
        const nextIndex = room.totalMessagesSent % room.players.length;
        if (room.totalMessagesSent >= (room.players.length * room.settings.turnsPerPlayer)) {
            io.to(data.roomId).emit('newWord', { sender: data.name, word: data.word });
            io.to(data.roomId).emit('startVoting', { players: room.players });
        } else {
            io.to(data.roomId).emit('newWord', { sender: data.name, word: data.word, nextTurn: room.players[nextIndex].name });
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
            io.to(data.roomId).emit('roundResult', {
                isCorrect: room.imposters.includes(votedOutId),
                votedOutName: room.players.find(p => p.id === votedOutId).name,
                imposters: room.players.filter(p => room.imposters.includes(p.id)).map(p => p.name),
                word: room.word
            });
            room.status = 'lobby';
            room.totalMessagesSent = 0;
            room.votes = {};
        }
    });

    socket.on('disconnect', () => {
        for (const roomId in rooms) {
            const room = rooms[roomId];
            const playerIndex = room.players.findIndex(p => p.id === socket.id);
            if (playerIndex !== -1) {
                const wasImposter = room.imposters.includes(socket.id);
                room.players.splice(playerIndex, 1);
                if (room.hostId === socket.id) {
                    io.to(roomId).emit('error', 'Värden lämnade.');
                    delete rooms[roomId];
                } else if (room.status === 'playing' && wasImposter) {
                    io.to(roomId).emit('error', 'Impostern lämnade! Matchen slut.');
                    room.status = 'lobby';
                    io.to(roomId).emit('forceLobby');
                } else {
                    io.to(roomId).emit('updatePlayers', { players: room.players });
                }
            }
        }
    });
});

http.listen(3000, () => console.log('Blykio Server: 3000'));
