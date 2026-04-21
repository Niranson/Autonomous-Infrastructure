const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const { exec } = require('child_process');
const path = require('path');

const app = express();
app.use(express.json());

app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'index.html')));

const server = http.createServer(app);
const io = new Server(server);

app.post('/update', (req, res) => {
    io.emit('stats_update', req.body);
    res.sendStatus(200);
});

app.post('/api/control', (req, res) => {
    const { action, command } = req.body;
    let finalCmd = "";

    if (action === 'RESET') {
        finalCmd = 'kubectl scale deployment vote-service --replicas=1';
    } else if (action === 'MANUAL') {
        finalCmd = command; // Execute the exact command from the text area
    }

    if (finalCmd) {
        console.log(`Executing: ${finalCmd}`);
        exec(finalCmd, (err) => {
            if (err) console.error(`Exec Error: ${err}`);
        });
        res.json({ status: "Executed" });
    }
});

server.listen(5000, () => console.log('Sentinel Console: http://localhost:5000'));