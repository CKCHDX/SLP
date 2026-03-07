# Getting Started with SLP

## Project Overview

The **Secure Line Protocol (SLP)** project consists of two main modules:

### 1. CSH (Central Server Hub) Module `/csh`

**Purpose**: Service orchestration and management

**Responsibilities**:
- Service lifecycle management (start/stop/restart)
- Web-based control interfaces (DCC, SLC)
- Process monitoring and health checks
- Configuration management
- User interaction through web dashboard

**Key Components**:
- `core/`: Core server logic
- `interfaces/`: Web dashboards (DCC, SLC) and REST APIs
- `services/`: Service management system
- `utils/`: Logging, system monitoring

---

### 2. SLP (Secure Line Protocol) Module `/slp`

**Purpose**: Cryptographic communication protocol

**Responsibilities**:
- Packet creation and parsing
- Multi-layer encryption (TLS, DTLS, Noise)
- UDP transport and reliability
- HTTPS ↔ SLP conversion for browser support (gateway)
- Local HTTPS proxy for desktop app support
- Client library for service communication

**Key Components**:
- `protocol/`: Core SLP protocol implementation
- `encryption/`: Cryptographic layer
- `transport/`: UDP and packet handling
- `gateway/`: Browser support via HTTPS
- `proxy/`: Desktop app support via local proxy
- `client/`: Client library for services

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

### Step 1: Clone Repository

```bash
git clone https://github.com/CKCHDX/SLP.git
cd SLP
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Create Configuration Files

Configuration files should be placed in the `config/` directory:

```bash
# Create config directory
mkdir -p config
```

See "Configuration" section below for details.

### Step 5: Generate SSL Certificates (Optional)

For local development:

```bash
# Generate self-signed certificates
python scripts/generate_certs.py
```

---

## Configuration

### CSH Configuration (`config/csh.yaml`)

```yaml
csh:
  name: "Oscyra Central Server Hub"
  version: "1.0.0"
  bind_ip: "0.0.0.0"
  base_port: 4270
  
services:
  klar:
    enabled: true
    sl_id: "klar-001"
    port: 4271
    executable: "../klar/server.py"
    auto_restart: true
    
  sverkan:
    enabled: true
    sl_id: "sverkan-001"
    port: 4272
    executable: "../sverkan/server.py"
    auto_restart: true
    
  upsum:
    enabled: true
    sl_id: "upsum-001"
    port: 4273
    executable: "../upsum/server.py"
    auto_restart: true

sl_protocol:
  encryption: "DTLS_1_3_AES_256_GCM"
  noise_protocol: true
  forward_secrecy: true
  
dashboard:
  enabled: true
  port: 9000
  allowed_ips:
    - "127.0.0.1"
    - "::1"
```

### SLP Protocol Configuration (`config/slp.yaml`)

```yaml
sl_protocol:
  version: "1.0.0"
  
encryption:
  default_algorithm: "DTLS_1_3_AES_256_GCM"
  enable_noise: true
  enable_tls: true
  enable_dtls: true
  
transport:
  protocol: "UDP"
  default_ports:
    - 4270  # Core SLP
    - 4271  # Klar
    - 4272  # Sverkan
    - 4273  # Upsum
  
gateway:
  enabled: true
  https_port: 443
  
local_proxy:
  enabled: true
  https_port: 8443
```

---

## Running the Project

### Start CSH (Central Server Hub)

```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Start CSH
python csh/csh.py
```

You should see:
```
DEBUG:csh.csh:Central Server Hub initialized
DEBUG:csh.csh:Config: config/csh.yaml
INFO:csh.csh:Starting Central Server Hub...
```

### Access Web Interfaces

Once CSH is running:

- **Dynamic Control Center (DCC)**: http://localhost:9000/dcc
  - Service management
  - Start/stop/restart services
  - Configuration
  
- **Status Log Center (SLC)**: http://localhost:9000/slc
  - Real-time service monitoring
  - Live log streaming
  - Performance metrics

---

## Project Structure Quick Reference

```
SLP/
├── csh/                          # CSH Module
│   ├── csh.py                   # Main entry point
│   ├── config.py                # Configuration manager
│   ├── core/                    # Core logic
│   ├── interfaces/              # Web interfaces (DCC, SLC)
│   ├── services/                # Service management
│   └── utils/                   # Utilities
│
├── slp/                          # SLP Module
│   ├── protocol/                # Core protocol
│   ├── encryption/              # Encryption layer
│   ├── transport/               # Transport layer
│   ├── gateway/                 # Gateway hub
│   ├── proxy/                   # Local proxy
│   ├── client/                  # Client library
│   └── utils/                   # Utilities
│
├── config/                       # Configuration files
├── tests/                        # Test suite
├── docs/                         # Documentation
├── scripts/                      # Utility scripts
├── requirements.txt              # Dependencies
└── ARCHITECTURE.md               # System design
```

---

## Development Workflow

### Creating a New Service

1. Define service in `config/csh.yaml`
2. CSH automatically detects and manages it
3. Service communicates via SLP protocol
4. No changes needed to SLP or CSH code

### Enhancing SLP Protocol

1. Modify code in `/slp` module
2. CSH automatically uses updated protocol
3. Add tests in `/tests` directory
4. Update `/docs/PROTOCOL.md`

### Adding CSH Features

1. Modify code in `/csh` module
2. Update web interfaces as needed
3. Leverage existing SLP interfaces
4. Add tests in `/tests` directory

---

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=csh --cov=slp

# Run specific test
pytest tests/unit/test_csh_core.py -v

# Run in watch mode (requires pytest-watch)
ptw tests/
```

---

## Code Quality

### Format Code

```bash
black csh/ slp/ tests/
```

### Check Style

```bash
flake8 csh/ slp/ tests/
```

### Type Checking

```bash
mypy csh/ slp/
```

---

## Troubleshooting

### CSH Won't Start

1. Check Python version: `python --version` (should be 3.10+)
2. Verify dependencies: `pip install -r requirements.txt`
3. Check config file exists: `config/csh.yaml`
4. Check ports are available: ports 9000, 4270-4273

### Web Interface Not Accessible

1. Ensure CSH is running
2. Check firewall allows localhost:9000
3. Try direct URL: `http://127.0.0.1:9000/dcc`
4. Check CSH logs for errors

### Services Won't Start

1. Verify service executable exists
2. Check service path in config is correct
3. Look for errors in SLC logs
4. Ensure service doesn't depend on external resources

---

## Next Steps

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design
2. Explore [docs/](docs/) for detailed documentation
3. Check [tests/](tests/) for usage examples
4. Start developing:
   - Implement CSH core server
   - Build SLP protocol layer
   - Create web interfaces
   - Add service management

---

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and add tests
3. Run tests: `pytest`
4. Format code: `black csh/ slp/`
5. Push and create pull request

---

## Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: See `/docs` directory
- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)

---

## License

See LICENSE file for details.
