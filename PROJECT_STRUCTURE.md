# SLP Project Structure - Modular Design

## Overview

The SLP project is organized with **modular separation** between **CSH (Central Server Hub)** and **SLP (Secure Line Protocol)**, while maintaining tight integration through well-defined interfaces.

## Directory Layout

```
SLP/
│
├── README.md                          # Project overview
├── ARCHITECTURE.md                    # System design documentation
├── PROJECT_STRUCTURE.md              # This file
├── requirements.txt                   # Python dependencies
├── setup.py                          # Installation configuration
│
├── csh/                              # *** CSH MODULE ***
│   ├── __init__.py
│   ├── csh.py                        # Main CSH entry point
│   ├── config.py                     # Configuration loader
│   │
│   ├── core/                         # CSH Core Logic
│   │   ├── __init__.py
│   │   ├── server.py                 # Main CSH server
│   │   ├── service_manager.py        # Service lifecycle management
│   │   ├── router.py                 # SL-ID based routing
│   │   ├── process_monitor.py        # Process health monitoring
│   │   └── crypto_manager.py         # Encryption key management
│   │
│   ├── interfaces/                   # Web Interfaces
│   │   ├── __init__.py
│   │   ├── web_server.py             # Flask/FastAPI server
│   │   │
│   │   ├── dcc/                      # Dynamic Control Center
│   │   │   ├── __init__.py
│   │   │   ├── api.py                # REST API endpoints
│   │   │   ├── handlers.py           # Request handlers
│   │   │   └── static/
│   │   │       ├── index.html
│   │   │       ├── app.js
│   │   │       ├── style.css
│   │   │       └── assets/
│   │   │
│   │   └── slc/                      # Status Log Center
│   │       ├── __init__.py
│   │       ├── api.py                # REST API endpoints
│   │       ├── websocket.py          # WebSocket for real-time updates
│   │       ├── handlers.py
│   │       └── static/
│   │           ├── index.html
│   │           ├── app.js
│   │           ├── style.css
│   │           └── assets/
│   │
│   ├── services/                     # Service Management
│   │   ├── __init__.py
│   │   ├── base_service.py           # Abstract base class
│   │   ├── service_loader.py         # Dynamic service loading
│   │   ├── process_handler.py        # Subprocess management
│   │   └── service_registry.py       # Service registry
│   │
│   └── utils/                        # Utilities
│       ├── __init__.py
│       ├── logger.py                 # Logging configuration
│       ├── system_monitor.py         # CPU/Memory monitoring
│       └── helpers.py                # General utilities
│
├── slp/                              # *** SLP MODULE ***
│   ├── __init__.py
│   │
│   ├── protocol/                     # Core SL Protocol
│   │   ├── __init__.py
│   │   ├── slp_core.py               # Main protocol implementation
│   │   ├── packet.py                 # Packet structure/parsing
│   │   ├── routing.py                # Protocol routing logic
│   │   ├── state_machine.py          # Connection state management
│   │   └── error_handling.py         # Protocol error handling
│   │
│   ├── encryption/                   # Encryption Layer
│   │   ├── __init__.py
│   │   ├── crypto.py                 # Encryption/Decryption
│   │   ├── key_manager.py            # Key generation/storage
│   │   ├── tls_handler.py            # TLS 1.3 support
│   │   ├── dtls_handler.py           # DTLS 1.3 support
│   │   └── noise_handler.py          # Noise protocol support
│   │
│   ├── transport/                    # Transport Layer
│   │   ├── __init__.py
│   │   ├── udp_transport.py          # UDP implementation
│   │   ├── connection_pool.py        # Connection management
│   │   ├── packet_assembler.py       # Handle fragmentation
│   │   └── retransmission.py         # Reliability logic
│   │
│   ├── gateway/                      # Gateway Hub (Browser Support)
│   │   ├── __init__.py
│   │   ├── gateway_server.py         # HTTPS ↔ SL translator
│   │   ├── https_handler.py          # HTTPS support
│   │   ├── sl_adapter.py             # SL Protocol adapter
│   │   └── session_manager.py        # Session handling
│   │
│   ├── proxy/                        # Local Proxy (Desktop Support)
│   │   ├── __init__.py
│   │   ├── local_proxy.py            # Local proxy server
│   │   ├── https_proxy.py            # HTTPS listener
│   │   ├── sl_connector.py           # SL Protocol connector
│   │   └── client_manager.py         # Client connection management
│   │
│   ├── client/                       # Client Libraries
│   │   ├── __init__.py
│   │   ├── slp_client.py             # Main client
│   │   ├── async_client.py           # Async/await support
│   │   ├── sync_client.py            # Synchronous support
│   │   └── connection.py             # Connection handling
│   │
│   └── utils/                        # Protocol Utilities
│       ├── __init__.py
│       ├── protocol_logger.py        # Protocol-level logging
│       ├── debug_tools.py            # Debugging utilities
│       └── performance_monitor.py    # Performance tracking
│
├── config/                           # Configuration Files
│   ├── csh.yaml                      # CSH configuration
│   ├── slp.yaml                      # SLP protocol configuration
│   ├── services.yaml                 # Service definitions
│   ├── encryption.yaml               # Encryption settings
│   └── logging.yaml                  # Logging configuration
│
├── tests/                            # Test Suite
│   ├── __init__.py
│   ├── conftest.py                   # Pytest configuration
│   │
│   ├── unit/
│   │   ├── test_csh_core.py
│   │   ├── test_slp_protocol.py
│   │   ├── test_encryption.py
│   │   └── test_routing.py
│   │
│   ├── integration/
│   │   ├── test_csh_slp_integration.py
│   │   ├── test_service_management.py
│   │   └── test_end_to_end.py
│   │
│   └── performance/
│       ├── test_throughput.py
│       ├── test_latency.py
│       └── test_encryption_perf.py
│
├── docs/                             # Documentation
│   ├── ARCHITECTURE.md               # System architecture
│   ├── API.md                        # API documentation
│   ├── PROTOCOL.md                   # Protocol specification
│   ├── DEPLOYMENT.md                 # Deployment guide
│   └── TROUBLESHOOTING.md            # Troubleshooting guide
│
├── scripts/                          # Utility Scripts
│   ├── setup.sh                      # Setup script (Linux/Mac)
│   ├── setup.ps1                     # Setup script (Windows)
│   ├── start_csh.sh                  # Start CSH (Linux/Mac)
│   ├── start_csh.ps1                 # Start CSH (Windows)
│   ├── generate_certs.py             # Certificate generation
│   └── migrate_config.py             # Configuration migration
│
└── .github/
    ├── workflows/
    │   ├── tests.yml                 # CI/CD tests
    │   ├── lint.yml                  # Code quality checks
    │   └── build.yml                 # Build workflow
    └── ISSUE_TEMPLATE/
        ├── bug_report.md
        └── feature_request.md

```

## Module Descriptions

### CSH Module (`/csh`)

**Purpose**: Central Server Hub - manages services, web interfaces, and orchestration.

**Responsibilities**:
- Service lifecycle management (start/stop/restart)
- Web-based control interfaces (DCC and SLC)
- Process monitoring and health checks
- Configuration management
- User interaction

**Key Components**:
- `core/`: Core CSH server logic
- `interfaces/`: Web dashboards and REST APIs
- `services/`: Service management system
- `utils/`: Logging, monitoring utilities

**External Dependencies**: 
- SLP module (for protocol handling)
- Flask/FastAPI (web framework)
- Psutil (system monitoring)

---

### SLP Module (`/slp`)

**Purpose**: Secure Line Protocol - handles all cryptographic communication and transport.

**Responsibilities**:
- Packet creation and parsing
- Encryption/decryption (TLS, DTLS, Noise)
- UDP transport and reliability
- HTTPS ↔ SLP conversion (gateway)
- Local proxy for desktop apps
- Client library for services

**Key Components**:
- `protocol/`: Core SLP protocol
- `encryption/`: Crypto layer (multi-algo support)
- `transport/`: UDP and packet handling
- `gateway/`: Browser support via HTTPS
- `proxy/`: Desktop app support via local proxy
- `client/`: Client library

**External Dependencies**:
- Cryptography library
- Socket/asyncio (built-in)
- uvloop (optional, performance)

---

## Integration Points

### CSH → SLP

CSH uses SLP for:

1. **Protocol Initialization**
   ```python
   from slp.protocol import SLPCore
   self.slp = SLPCore(config)
   ```

2. **Creating SL Connections**
   ```python
   connection = self.slp.create_connection(sl_id, target_port)
   ```

3. **Routing Packets**
   ```python
   self.slp.route_packet(packet, destination_id)
   ```

### SLP → CSH

SLP interfaces with CSH through callbacks:

1. **Service Registration**
   ```python
   slp.register_service_callback(on_service_request)
   ```

2. **Event Notifications**
   ```python
   slp.on_connection_established(callback)
   slp.on_packet_received(callback)
   ```

3. **Configuration**
   ```python
   slp.apply_config(csh_config)
   ```

---

## Dependency Graph

```
csh/
├── depends on: slp (protocol, encryption, transport)
├── depends on: Flask/FastAPI (web framework)
├── depends on: Psutil (system monitoring)
└── depends on: PyYAML (config parsing)

slp/
├── depends on: cryptography (encryption)
├── depends on: asyncio (async support)
└── depends on: optional: uvloop (performance)
```

---

## Data Flow

### Service Request Flow

```
DCC Control Interface
    ↓
CSH Core (service_manager.py)
    ↓
CSH Router (router.py)
    ↓
SLP Protocol (protocol/slp_core.py)
    ↓
SLP Encryption (encryption/crypto.py)
    ↓
SLP Transport (transport/udp_transport.py)
    ↓
Network (UDP 4270-4273)
    ↓
[Destination Service]
```

---

## File Ownership

| Directory | Owned By | Purpose |
|-----------|----------|---------|
| `/csh` | CSH Team | Service management and web interfaces |
| `/slp` | Protocol Team | Cryptographic communication |
| `/config` | Both | Shared configuration files |
| `/tests` | QA Team | Test suite |
| `/docs` | Tech Lead | Documentation |
| `/scripts` | DevOps | Deployment and setup |

---

## Development Workflow

### When Adding a New Service

1. Define service in `config/services.yaml`
2. CSH automatically loads and manages it
3. Service communicates via SLP protocol
4. No SLP module changes needed

### When Enhancing SLP Protocol

1. Update code in `/slp` module
2. CSH automatically uses new protocol version
3. Add tests in `/tests`
4. Update `/docs/PROTOCOL.md`
5. No CSH module changes needed (unless adding new features)

### When Adding New CSH Features

1. Add code in `/csh` module
2. Update web interfaces in `/csh/interfaces`
3. Use existing SLP interfaces
4. Add tests in `/tests`
5. No SLP module changes needed

---

## Getting Started

### Installation

```bash
# Clone repository
git clone https://github.com/CKCHDX/SLP.git
cd SLP

# Install dependencies
pip install -r requirements.txt

# Generate configuration
python scripts/setup.py

# Generate SSL certificates
python scripts/generate_certs.py
```

### Running CSH

```bash
# Start the Central Server Hub
python csh/csh.py

# Access interfaces
# DCC: http://localhost:9000/dcc
# SLC: http://localhost:9000/slc
```

---

## Best Practices

### CSH Development

- Keep business logic in CSH, protocol logic in SLP
- Use SLP interfaces consistently
- Document all REST API endpoints
- Maintain web UI responsiveness
- Handle errors gracefully

### SLP Development

- Keep protocol concerns isolated
- Provide clean client interfaces
- Test encryption thoroughly
- Document packet formats
- Monitor performance metrics

### Integration

- Define clear module boundaries
- Use dependency injection
- Maintain backward compatibility
- Version APIs properly
- Document integration points

---

## Next Steps

1. ✅ Create folder structure (this document)
2. ⏳ Initialize module `__init__.py` files
3. ⏳ Create base classes (CSH and SLP)
4. ⏳ Implement CSH core server
5. ⏳ Implement SLP protocol core
6. ⏳ Create web interfaces (DCC, SLC)
7. ⏳ Add service management
8. ⏳ Build encryption layer
9. ⏳ Implement transport layer
10. ⏳ Create integration tests

---

## Questions?

Refer to:
- `ARCHITECTURE.md` - System design
- `docs/PROTOCOL.md` - Protocol details (to be created)
- `docs/API.md` - API documentation (to be created)
