# SLP - Simplified Start Guide

## Project Approach

Before integrating SLP into all services, we'll start with a **minimal proof-of-concept** to validate the core protocol works.

---

## Phase 0: Minimal Working Prototype

### Setup

**Server A (Your Main Server)**
- SLP server implementation
- Temporary HTML/CSS/JS frontend for testing
- UDP listener on port 4270

**Client Program (Windows)**
- Qt WebEngine-based client (existing)
- SLP client library integration
- Custom address support (e.g., `slp://klar.local`)

---

## Current State: HTTP Works

```
[Qt WebEngine Client]
    ↓ HTTP
[Server A]
```

This currently works with regular HTTP.

---

## Goal: Make SLP Work

```
[Qt WebEngine Client + SLP Client]
    ↓ SLP Protocol (encrypted UDP)
[Server A + SLP Server]
    ↓
[HTML/CSS/JS Frontend]
```

---

## Implementation Steps

### Step 1: Basic SLP Server (Week 1)

**Location**: `slp/protocol/slp_server.py`

**Requirements**:
- Listen on UDP port 4270
- Accept SLP connections
- Basic packet parsing (no encryption yet)
- Return simple response

**Test**:
```python
python slp/protocol/slp_server.py
# Server listening on 0.0.0.0:4270
```

---

### Step 2: Basic SLP Client (Week 1)

**Location**: `slp/client/simple_client.py`

**Requirements**:
- Connect to SLP server via UDP
- Send basic request
- Receive response
- No encryption initially

**Test**:
```python
from slp.client import SimpleSLPClient

client = SimpleSLPClient('localhost', 4270)
response = client.send('Hello SLP')
print(response)  # Should get response from server
```

---

### Step 3: Packet Format (Week 1)

**Location**: `slp/protocol/packet.py`

**Basic Packet Structure**:
```
+------------------+
| Version (1 byte) |  0x01
+------------------+
| Type (1 byte)    |  0x01 = Request, 0x02 = Response
+------------------+
| Length (2 bytes) |  Payload length
+------------------+
| Payload (N bytes)|  Data
+------------------+
```

---

### Step 4: Qt Client Integration (Week 2)

**For Your Windows Client**:

```cpp
// In your Qt WebEngine client
#include "slp_client_wrapper.h"

SLPClient* slpClient = new SLPClient("klar.local", 4270);
slpClient->connect();

// When loading URL
if (url.startsWith("slp://")) {
    QString response = slpClient->sendRequest(url);
    webEngine->setHtml(response);
}
```

**Python wrapper** (callable from C++ via subprocess or library):
```python
# slp_client_wrapper.py
from slp.client import SimpleSLPClient

def send_request(host, port, data):
    client = SimpleSLPClient(host, port)
    return client.send(data)
```

---

### Step 5: Add Encryption (Week 2-3)

**Once basic communication works**, add encryption:

1. **AES-256-GCM** (simplest first)
2. **Key exchange** via Diffie-Hellman
3. **TLS 1.3** wrapper (optional)
4. **DTLS 1.3** for UDP (advanced)
5. **Noise Protocol** (final layer)

---

## Directory Structure for POC

```
SLP/
├── slp/
│   ├── protocol/
│   │   ├── slp_server.py      # Simple UDP server
│   │   ├── packet.py          # Packet format
│   │   └── handler.py         # Request handling
│   │
│   └── client/
│       ├── simple_client.py   # Basic Python client
│       └── client_wrapper.py  # C++ callable wrapper
│
├── examples/
│   ├── server.py              # Run simple server
│   ├── client.py              # Test client
│   └── test_connection.py     # Connection test
│
└── frontend/
    └── test.html              # Simple HTML page for testing
```

---

## Testing Flow

### Test 1: Python to Python

```bash
# Terminal 1 - Start server
python examples/server.py

# Terminal 2 - Test client
python examples/client.py
# Expected: "Connection successful"
```

### Test 2: Qt Client to Server

```bash
# Terminal 1 - Start server
python examples/server.py

# Your Windows machine - Run Qt client
klar.exe
# Navigate to: slp://klar.local
# Expected: HTML page loads
```

---

## Custom Address Format

**SLP Address Format**:
```
slp://[service].[domain]:[port]/[path]

Examples:
slp://klar.local:4270/
slp://klar.local:4270/search?q=test
slp://sverkan.oscyra.solutions:4272/
```

**Client Parsing**:
```python
def parse_slp_url(url):
    # slp://klar.local:4270/search?q=test
    parts = url.split('://', 1)[1]  # klar.local:4270/search?q=test
    host_port, path = parts.split('/', 1)  # klar.local:4270, search?q=test
    host, port = host_port.split(':')  # klar.local, 4270
    return host, int(port), '/' + path
```

---

## Success Criteria

### Milestone 1: Basic Communication (Week 1)
- ✅ Server listens on UDP 4270
- ✅ Client can connect
- ✅ Simple request/response works
- ✅ No encryption (plaintext)

### Milestone 2: Qt Integration (Week 2)
- ✅ Qt client can use SLP
- ✅ Custom address format works
- ✅ HTML page loads via SLP
- ✅ Still no encryption

### Milestone 3: Encryption (Week 3)
- ✅ AES-256-GCM encryption works
- ✅ Key exchange implemented
- ✅ All communication encrypted
- ✅ Performance acceptable

### Milestone 4: Production Ready (Week 4+)
- ✅ Multiple encryption layers
- ✅ Error handling robust
- ✅ Performance optimized
- ✅ Ready for service integration

---

## Why This Approach?

1. **Validate Core Concept First**
   - Prove SLP works before complex integration
   - Test UDP communication reliability
   - Verify Qt client compatibility

2. **Incremental Complexity**
   - Start simple (no encryption)
   - Add encryption layer by layer
   - Each step is testable

3. **Faster Iteration**
   - No need for full CSH yet
   - Direct server-client testing
   - Quick debugging cycle

4. **Real-World Validation**
   - Test with actual Qt WebEngine
   - Verify Windows compatibility
   - Confirm custom addresses work

---

## Next Steps (Immediate)

1. **Create `slp/protocol/slp_server.py`**
   - Basic UDP server
   - Packet parsing
   - Simple response

2. **Create `slp/client/simple_client.py`**
   - UDP client
   - Send request
   - Receive response

3. **Create `examples/server.py`**
   - Launch server easily
   - Test connection

4. **Create `examples/client.py`**
   - Test client
   - Verify communication

5. **Create `frontend/test.html`**
   - Simple HTML page
   - Test response rendering

---

## Code Snippets to Implement

### Simple Server (examples/server.py)

```python
import socket

HOST = '0.0.0.0'
PORT = 4270

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.bind((HOST, PORT))
    print(f"SLP Server listening on {HOST}:{PORT}")
    
    while True:
        data, addr = sock.recvfrom(4096)
        print(f"Received from {addr}: {data}")
        
        # Echo back
        response = b"HTTP/1.1 200 OK\r\n" + \
                   b"Content-Type: text/html\r\n\r\n" + \
                   b"<h1>SLP Works!</h1>"
        sock.sendto(response, addr)
```

### Simple Client (examples/client.py)

```python
import socket

HOST = 'localhost'
PORT = 4270

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    message = b"GET / HTTP/1.1\r\nHost: klar.local\r\n\r\n"
    sock.sendto(message, (HOST, PORT))
    
    response, addr = sock.recvfrom(4096)
    print(f"Response from {addr}:")
    print(response.decode())
```

---

## Timeline

| Week | Task | Deliverable |
|------|------|-------------|
| 1 | Basic UDP server + client | Python-to-Python works |
| 2 | Qt client integration | Qt client can use SLP |
| 3 | Add AES-256-GCM encryption | Encrypted communication |
| 4 | Multiple encryption layers | Production-ready |
| 5+ | CSH integration | Full system |

---

## Questions to Answer

1. **Does UDP work reliably for your use case?**
   - Test with large payloads
   - Test with packet loss simulation
   - Measure latency

2. **Can Qt WebEngine work with custom protocol?**
   - Intercept `slp://` URLs
   - Convert to SLP requests
   - Render responses

3. **Is performance acceptable?**
   - Measure request/response time
   - Compare with HTTP
   - Identify bottlenecks

4. **Does encryption add too much overhead?**
   - Measure encryption time
   - Test with different algorithms
   - Optimize if needed

---

## Success = Proof of Concept Works

Once this simple setup works:
- ✅ SLP protocol validated
- ✅ Qt client integration confirmed
- ✅ Custom addresses working
- ✅ Encryption feasible

**Then** we can confidently build the full CSH + multi-service architecture.

---

*Start small, validate fast, scale confidently.* 🚀
