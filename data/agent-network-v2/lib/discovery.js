const dgram = require('dgram');
const crypto = require('crypto');
const EventEmitter = require('events');

const BROADCAST_PORT = 18790;
const BROADCAST_INTERVAL = 5000;

class LocalDiscovery extends EventEmitter {
  constructor(nodeId, port) {
    super();
    this.nodeId = nodeId;
    this.port = port;
    this.socket = null;
    this.peers = new Map();
  }
  
  start() {
    this.socket = dgram.createSocket({ type: 'udp4', reuseAddr: true });
    
    this.socket.on('message', (msg, rinfo) => {
      try {
        const data = JSON.parse(msg.toString());
        if (data.nodeId !== this.nodeId) {
          this.peers.set(data.nodeId, { ...data, ip: rinfo.address });
          this.emit('peerFound', data);
        }
      } catch (e) {}
    });
    
    this.socket.on('error', (err) => {
      console.log('Discovery socket error:', err.message);
    });
    
    this.socket.bind(BROADCAST_PORT, () => {
      this.socket.setBroadcast(true);
      console.log('Local discovery started on port', BROADCAST_PORT);
      this.broadcast();
    });
    
    this.interval = setInterval(() => this.broadcast(), BROADCAST_INTERVAL);
  }
  
  broadcast() {
    const message = JSON.stringify({
      nodeId: this.nodeId,
      port: this.port,
      type: 'openclaw-agent',
      version: '1.0.6',
      services: ['p2p', 'chat', 'skills']
    });
    
    const buffer = Buffer.from(message);
    
    this.socket.send(buffer, 0, buffer.length, BROADCAST_PORT, '255.255.255.255', (err) => {
      if (err) console.log('Broadcast error:', err.message);
    });
  }
  
  getPeers() {
    return Array.from(this.peers.values());
  }
  
  stop() {
    if (this.interval) clearInterval(this.interval);
    if (this.socket) this.socket.close();
  }
}

class LocalNetworkDiscovery {
  constructor(p2p) {
    this.p2p = p2p;
    this.discovery = null;
  }
  
  start() {
    this.discovery = new LocalDiscovery(this.p2p.peerId, this.p2p.port);
    this.discovery.start();
    
    this.discovery.on('peerFound', async (peer) => {
      console.log(`Found local peer: ${peer.nodeId} at ${peer.ip}:${peer.port}`);
      try {
        await this.p2p.connect(`${peer.ip}:${peer.port}`);
      } catch (e) {}
    });
  }
  
  getPeers() {
    if (this.discovery) {
      return this.discovery.getPeers();
    }
    return [];
  }
  
  stop() {
    if (this.discovery) {
      this.discovery.stop();
    }
  }
}

module.exports = { LocalDiscovery, LocalNetworkDiscovery };
