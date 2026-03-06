# Secure Line Protocol (SL)

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org) [![License](https://img.shields.io/badge/License-MIT-green)](LICENSE) [![Status](https://img.shields.io/badge/Status-Active%20Development-yellow)](https://github.com/CKCHDX/SLP)

**Secure Line Protocol (SL)** is a custom UDP-based application-layer protocol designed for ultra-fast, secure client-server and hybrid P2P communication within the Oscyra.solutions ecosystem.

## 🎯 Purpose

SL Protocol replaces plain HTTP/HTTPS with military-grade encrypted communication for:
- **klar.oscyra.solutions** - Search engine
- **upsum.oscyra.solutions** - Knowledge platform  
- **sverkan.oscyra.solutions** - Cloud desktop/education platform

Addresses dynamic IP challenges with custom `sl://unique-id.oscyra.solutions` addressing scheme.

## 🏗️ Architecture

```
Browser                    SL Gateway Hub               Backend Services
  |                              |                            |
  | HTTPS upsum.oscyra.solutions |                            |
  |----------------------------->|                            |
  |                              | SL Protocol (UDP 4271)     |
  |                              |--------------------------->|
  |                              |    upsum.oscyra.solutions  |
  |                              |    (internal SL-ID)        |
  |                              |                            |
  |                              | SL Protocol Response       |
  |                              |<---------------------------|
  | HTTPS Response               |                            |
  |<-----------------------------|                            |
```

### How It Works

1. **Browser Layer**: Users access `https://upsum.oscyra.solutions` normally
2. **Gateway Hub**: Translates HTTPS → SL Protocol (encrypted UDP)
3. **Backend Services**: Process requests using SL Protocol internally
4. **Response**: Gateway translates SL → HTTPS back to browser

### Why This Design?

**Problem**: Browsers only speak HTTP/HTTPS/WebSocket - cannot use custom UDP protocols.

**Solution**: SL Gateway Hub acts as protocol translator:
- **Public-facing**: Accepts HTTPS requests from browsers
- **Internal**: Translates to SL protocol and routes to backend services via encrypted UDP
- **Benefits**: Military-grade encryption between services while maintaining browser compatibility

## 🚀 Features

| Feature | Status |
|---------|--------|
| Custom `sl://` addressing | ✅ Planned |
| Hybrid P2P + Server | ✅ Planned |
| DTLS 1.3 Encryption | ✅ Planned |
| Noise Protocol Keys | ✅ Planned |
| NAT Traversal (ICE) | ✅ Planned |
| Binary Framing | ✅ Planned |
| HTTP→SL Gateway | ✅ Priority |
| Async Python (10k+ pkt/s) | ✅ Planned |

## 📦 Packet Format

**24-byte header structure:**
```
[Ver:1][Type:1][Seq:4][SL-ID:8][Len:2][Chk:2][Payload][AuthTag:16]
```

**Packet Types:**
- `0` = Handshake
- `1` = Data
- `2` = ACK
- `3` = Pong
- `4` = Keepalive

## 🔐 Security Architecture (Military-Grade)

### Encryption Layers

```
Browser → [TLS 1.3] → Gateway Hub → [DTLS 1.3 + Noise] → Services
         (Public)                    (Private Network)
```

**Triple-Layer Security:**
1. **External**: TLS 1.3 with Let's Encrypt certificates (browser → gateway)
2. **Internal**: SL protocol with DTLS 1.3 (gateway → backends)
3. **Application**: Noise Protocol with X25519 key exchange

### Security Comparison

| Feature | HTTP/HTTPS | SL Protocol |
|---------|------------|-------------|
| Encryption | TLS only | TLS + DTLS + Noise (triple) |
| Transport | TCP (slower) | UDP (3x faster) |
| DDoS Protection | Limited | Custom rate limiting + binary |
| NAT Traversal | N/A | Built-in ICE |
| Backend Exposure | Direct IPs exposed | Hidden behind gateway |
| Authentication | Certificate only | Certificate + mutual auth + PKI |

## 📁 Project Structure

```
SLP/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── requirements.txt             # Python dependencies
├── Makefile                     # Build automation
├── .gitignore                   # Git excludes
├── .env.example                 # Configuration template
│
├── src/
│   ├── protocol/               # Core SL protocol
│   │   ├── packet.py           # Binary packet framing
│   │   ├── crypto.py           # DTLS + Noise encryption
│   │   ├── addressing.py       # SL-ID resolver
│   │   └── nat.py              # ICE/STUN NAT traversal
│   │
│   ├── gateway/                # HTTP→SL Bridge (CRITICAL)
│   │   ├── hub.py              # Main gateway server
│   │   ├── router.py           # Domain→SL-ID mapping
│   │   └── websocket.py        # WebSocket support
│   │
│   ├── server/                 # Backend SL server
│   │   ├── core.py             # UDP listener
│   │   └── registry.py         # SL-ID registration
│   │
│   └── client/                 # Client library
│       ├── connector.py        # SL client
│       └── browser.py          # PyQt6 test client
│
├── config/
│   ├── gateway.conf            # Gateway settings
│   ├── server.conf             # Backend configuration
│   └── domains.yaml            # Oscyra domain mappings
│
├── tests/                      # Unit tests
├── scripts/                    # Deployment scripts
└── docs/                       # Documentation
```

## 🔧 Installation

### Prerequisites
- Python 3.11+
- Linux (production) or Windows (development)
- Domain: oscyra.solutions with DNS access

### Quick Setup

```bash
# Clone repository
git clone https://github.com/CKCHDX/SLP.git
cd SLP

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

```txt
cryptography>=42.0.0
pynacl>=1.5.0
aiortc>=1.5.0
scapy>=2.5.0
asyncio-mqtt>=0.12.0
```

## 📝 Configuration

### Domain Mapping (`config/domains.yaml`)

```yaml
services:
  - domain: upsum.oscyra.solutions
    sl_id: "upsum-main-001"
    backend_ip: "192.168.1.100"
    backend_port: 4271
    
  - domain: klar.oscyra.solutions
    sl_id: "klar-search-001"
    backend_ip: "192.168.1.101"
    backend_port: 4271
    
  - domain: sverkan.oscyra.solutions
    sl_id: "sverkan-edu-001"
    backend_ip: "192.168.1.102"
    backend_port: 4271
```

### DNS Setup (Netlify/Cloudflare)

```
# All domains point to Gateway IP
upsum.oscyra.solutions    → A record → Gateway IP (e.g., 203.0.113.50)
klar.oscyra.solutions     → A record → Gateway IP (same)
sverkan.oscyra.solutions  → A record → Gateway IP (same)
sl.oscyra.solutions       → A record → Gateway IP (API endpoint)
```

## 🚀 Usage

### Starting Gateway Hub

```bash
# Start SL Gateway (HTTPS → SL translator)
python src/gateway/hub.py --config config/gateway.conf

# Start Backend Service
python src/server/core.py --config config/server.conf --sl-id upsum-main-001
```

### Browser Access (Standard Users)

Users simply visit:
- `https://upsum.oscyra.solutions`
- `https://klar.oscyra.solutions`
- `https://sverkan.oscyra.solutions`

**They never interact with SL directly** - gateway handles translation automatically.

### Native Client (Advanced)

```python
from src.client.connector import SLConnector

# Direct SL protocol connection
conn = SLConnector("sl://upsum-main-001.oscyra.solutions")
response = conn.send({"query": "test"})
print(response)
```

## 🧪 Testing

```bash
# Run unit tests
pytest tests/ -v

# Test packet framing
pytest tests/test_packet.py

# Test encryption
pytest tests/test_crypto.py

# Test gateway routing
pytest tests/test_gateway.py
```

## 🛤️ Development Roadmap

### Phase 1: Core Protocol (Week 1)
- [ ] Binary packet format implementation
- [ ] DTLS 1.3 encryption layer
- [ ] SL-ID addressing system
- [ ] Basic UDP socket handling

### Phase 2: Gateway Hub (Week 2) ⭐ **PRIORITY**
- [ ] HTTPS server (port 443)
- [ ] HTTP → SL protocol translator
- [ ] Domain → SL-ID router
- [ ] WebSocket support for real-time

### Phase 3: Backend Integration (Week 3)
- [ ] Integrate with Upsum backend
- [ ] Integrate with Klar backend
- [ ] Integrate with Sverkan backend
- [ ] Performance testing (10k+ req/s)

### Phase 4: Production Deployment (Week 4)
- [ ] Let's Encrypt SSL certificates
- [ ] Cloudflare Tunnel setup
- [ ] Monitoring and logging
- [ ] Load balancing

### Future Enhancements
- [ ] P2P NAT traversal (ICE)
- [ ] Mobile client (Android)
- [ ] C++ port for ultra-low latency
- [ ] WebRTC integration

## 📊 Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Gateway Latency | <5ms | 🔄 Testing |
| Backend Latency | <10ms | 🔄 Testing |
| Throughput | 10k+ req/s | 🔄 Testing |
| Packet Loss | <0.1% | 🔄 Testing |
| Encryption Overhead | <2ms | 🔄 Testing |

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add unit tests for new features
- Update documentation
- Security review required for crypto changes

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

```
Secure Line Protocol (SL) - Copyright (c) 2026 Alex Jonsson (CKCHDX)
Built for Oscyra.solutions ecosystem
```

## 🙏 Acknowledgments

- **Inspired by**: WireGuard, QUIC, Noise Protocol Framework
- **Cryptography**: libsodium, cryptography.io
- **P2P**: aiortc, ICE/STUN protocols
- **Testing**: Scapy, Wireshark, pytest
- **Infrastructure**: Cloudflare, Netlify, oscyra.solutions

## 📞 Contact & Support

- **GitHub**: [@CKCHDX](https://github.com/CKCHDX)
- **Website**: [oscyra.solutions](https://oscyra.solutions)
- **Issues**: [GitHub Issues](https://github.com/CKCHDX/SLP/issues)

---

⭐ **Star this repo** if you find it useful! | 🐛 **Report bugs** via Issues | 💬 **Questions?** Open a Discussion

**Built with 🔐 in Jönköping, Sweden**
