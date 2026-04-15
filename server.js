const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const app = express();
const server = http.createServer(app);
const io = new Server(server);

// --- ORDLISTOR (100 per kategori) ---
const categories = {
    "Animals": ["Lejon", "Tiger", "Elefant", "Giraff", "Zebra", "Hund", "Katt", "Häst", "Ko", "Gris", "Apa", "Björn", "Varg", "Räv", "Älg", "Rådjur", "Kanin", "Hamster", "Marsvin", "Råtta", "Mus", "Fladdermus", "Örn", "Hök", "Uggla", "Pingvin", "Struts", "Kråka", "Skata", "Duvhök", "Svan", "Anka", "Gås", "Krokodil", "Orm", "Ödla", "Sköldpadda", "Groda", "Padda", "Lax", "Abborre", "Gädda", "Haj", "Val", "Delfin", "Säl", "Utter", "Bäver", "Ekorre", "Igelkott", "Mullvad", "Grävling", "Lo", "Järv", "Ren", "Myskoxe", "Sjöko", "Noshörning", "Flodhäst", "Gorilla", "Schimpans", "Orangutang", "Lemur", "Koala", "Känguru", "Vombat", "Platypus", "Panda", "Isbjörn", "Svartbjörn", "Grizzly", "Tvättbjörn", "Skunk", "Hyena", "Gepard", "Leopard", "Panter", "Jaguar", "Puma", "Lodjur", "Surikat", "Piggsvin", "Myrslok", "Bältdjur", "Sengångare", "Tukan", "Kolibri", "Papegoja", "Flamingo", "Pelikan", "Albatross", "Mås", "Tärna", "Lunnefågel", "Kalkon", "Kyckling", "Tjäder", "Orre", "Fasan"],
    "Food": ["Pizza", "Burgare", "Sushi", "Taco", "Pasta", "Köttbullar", "Pannkaka", "Våffla", "Omelett", "Sallad", "Soppa", "Gryta", "Lasagne", "Risotto", "Paella", "Kebab", "Falafel", "Hotdog", "Smörgås", "Gröt", "Yoghurt", "Filmjölk", "Müsli", "Ägg", "Bacon", "Korv", "Biff", "Kycklingfilé", "Laxfilé", "Torsk", "Räkor", "Kräftor", "Hummer", "Musslor", "Bläckfisk", "Potatis", "Ris", "Bulgur", "Quinoa", "Couscous", "Pommes", "Pasta", "Bröd", "Knäckebröd", "Ost", "Skinka", "Salami", "Leverpastej", "Kaviar", "Smör", "Margarin", "Mjölk", "Grädde", "Gräddfil", "Creme Fraiche", "Glass", "Tårta", "Kaka", "Bulle", "Muffin", "Choklad", "Godis", "Chips", "Popcorn", "Nötter", "Äpple", "Banan", "Päron", "Apelsin", "Citron", "Lime", "Grapefrukt", "Melon", "Vattenmelon", "Ananas", "Mango", "Kiwi", "Persika", "Nektarin", "Plommon", "Körsbär", "Jordgubbe", "Hallon", "Blåbär", "Lingon", "Hjortron", "Tomat", "Gurka", "Paprika", "Lök", "Vitlök", "Morot", "Palsternacka", "Sjögräs", "Rödbeta", "Broccoli", "Blomkål", "Spenat", "Ärtor", "Majs"],
    "Famous People": ["Zlatan", "Avicii", "Abba", "Gustav Vasa", "Astrid Lindgren", "Alfred Nobel", "Ingmar Bergman", "Greta Thunberg", "Elon Musk", "Bill Gates", "Steve Jobs", "Mark Zuckerberg", "Jeff Bezos", "Barack Obama", "Donald Trump", "Joe Biden", "Vladimir Putin", "Angela Merkel", "Nelson Mandela", "Dalai Lama", "Påven", "Drottning Elizabeth", "Prinsessan Victoria", "Kungen", "Albert Einstein", "Isaac Newton", "Charles Darwin", "Marie Curie", "Stephen Hawking", "Leonardo da Vinci", "Michelangelo", "Pablo Picasso", "Vincent van Gogh", "Salvador Dali", "William Shakespeare", "Ernest Hemingway", "J.K. Rowling", "Stephen King", "Michael Jackson", "Elvis Presley", "Freddie Mercury", "Madonna", "Beyonce", "Taylor Swift", "Ed Sheeran", "Justin Bieber", "Rihanna", "Drake", "Eminem", "Kanye West", "Brad Pitt", "Angelina Jolie", "Johnny Depp", "Tom Cruise", "Leonardo DiCaprio", "Meryl Streep", "Tom Hanks", "Robert De Niro", "Al Pacino", "Morgan Freeman", "Cristiano Ronaldo", "Lionel Messi", "Usain Bolt", "Michael Jordan", "Tiger Woods", "Roger Federer", "Serena Williams", "Muhammad Ali", "Mike Tyson", "Conor McGregor", "PewDiePie", "MrBeast", "Kylie Jenner", "Kim Kardashian", "Oprah Winfrey", "Ellen De Generes", "Gordon Ramsay", "Jamie Oliver", "Marilyn Monroe", "Audrey Hepburn", "Charlie Chaplin", "Walt Disney", "Neil Armstrong", "Yuri Gagarin", "Christopher Columbus", "Marco Polo", "Vasco da Gama", "Julius Caesar", "Alexander den Store", "Napoleon", "Abraham Lincoln", "Winston Churchill", "Mahatma Gandhi", "Martin Luther King", "Mother Teresa", "Anne Frank", "Cleopatra", "Mozart", "Beethoven", "Bach"],
    "Objects": ["Bord", "Stol", "Soffa", "Säng", "Garderob", "Hylla", "Skrivbord", "Fåtölj", "Pall", "Byrå", "Lampa", "Spegel", "Matta", "Gardin", "Kudde", "Täcke", "Lakan", "Handduk", "Tvål", "Schampo", "Tandborste", "Tandkräm", "Kam", "Borste", "Hårtork", "Rakhyvel", "Glas", "Tallrik", "Bestick", "Kniv", "Gaffel", "Sked", "Kastrull", "Stekpanna", "Ugn", "Spis", "Mikro", "Kylskåp", "Frys", "Diskmaskin", "Tvättmaskin", "Torktumlare", "Dammsugare", "Strykjärn", "TV", "Dator", "Mobil", "Surfplatta", "Hörlurar", "Högtalare", "Kamera", "Klocka", "Väckarklocka", "Armbandsur", "Glasögon", "Solglasögon", "Paraply", "Väska", "Ryggsäck", "Plånbok", "Nycklar", "Cykel", "Bil", "Buss", "Tåg", "Flygplan", "Båt", "Hammare", "Skruvmejsel", "Tång", "Såg", "Borr", "Spik", "Skruv", "Lim", "Tejp", "Sax", "Penna", "Papper", "Block", "Bok", "Tidning", "Karta", "Kompass", "Ficklampa", "Batteri", "Laddare", "Sladd", "Kontakt", "Knapp", "Blixtlås", "Nål", "Tråd", "Garn", "Tyg", "Parfym", "Smink", "Smycke", "Ring", "Halsband", "Örhänge"],
};

let rooms = {};

io.on('connection', (socket) => {
    socket.on('createMatch', (data) => {
        const roomId = Math.random().toString(36).substring(7).toUpperCase();
        rooms[roomId] = {
            id: roomId,
            admin: socket.id,
            players: [{ id: socket.id, name: data.name }],
            settings: data.settings,
            status: 'lobby',
            chat: [],
            imposters: [],
            word: '',
            turn: 0,
            rounds: 0
        };
        socket.join(roomId);
        socket.emit('matchCreated', rooms[roomId]);
        io.emit('publicMatches', Object.values(rooms).filter(r => r.settings.isPublic && r.status === 'lobby'));
    });

    socket.on('joinMatch', (data) => {
        const room = rooms[data.code];
        if (room && room.players.length < room.settings.maxPlayers) {
            room.players.push({ id: socket.id, name: data.name });
            socket.join(data.code);
            io.to(data.code).emit('updatePlayers', room.players);
            if(room.players.length == room.settings.maxPlayers) {
                // Auto-start om man vill här
            }
        }
    });

    socket.on('startGame', (roomId) => {
        const room = rooms[roomId];
        if (!room) return;

        const catWords = categories[room.settings.category];
        room.word = catWords[Math.floor(Math.random() * catWords.length)];
        room.status = 'playing';

        // Slumpa imposters
        let playerIndices = [...Array(room.players.length).keys()];
        for(let i=0; i < room.settings.imposterCount; i++) {
            let idx = playerIndices.splice(Math.floor(Math.random() * playerIndices.length), 1)[0];
            room.imposters.push(room.players[idx].id);
        }

        io.to(roomId).emit('gameStarted', {
            imposters: room.imposters,
            word: room.word,
            turnPlayer: room.players[0].name
        });
    });

    socket.on('sendWord', (data) => {
        const room = rooms[data.roomId];
        room.turn++;
        if(room.turn >= room.players.length) {
            room.turn = 0;
            room.rounds++;
        }

        io.to(data.roomId).emit('newWord', {
            sender: data.name,
            word: data.word,
            nextTurn: room.players[room.turn].name,
            isVoteTime: (room.rounds >= 2)
        });
    });
});

server.listen(3000, () => console.log('Blykio rullar på port 3000'));
