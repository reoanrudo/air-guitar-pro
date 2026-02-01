const { ExpressPeerServer } = require('peerjs-server');
const express = require('express');

const app = express();

app.use(express.static('public'));

const PORT = 3001;

const server = app.listen(PORT, () => {
  console.log(`PeerJS Server running on port ${PORT}`);
  console.log(`Signaling endpoint: http://localhost:${PORT}/peerjs`);
});

const peerServer = new ExpressPeerServer(server, {
  debug: true,
  path: '/peerjs'
});

peerServer.on('connection', (client) => {
  console.log(`Peer connected: ${client.getId()}`);
});

peerServer.on('disconnect', (client) => {
  console.log(`Peer disconnected: ${client.getId()}`);
});
