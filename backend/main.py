"""
============================================================================
FastAPI Backend for Live System Topology
Port of server.js with network discovery and host management
============================================================================
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
import subprocess
import socket
import re
import os
from typing import List, Optional
import asyncio
import uuid
from contextlib import asynccontextmanager

# ============================================================================
# Database Configuration
# ============================================================================

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://topology_user:topology_password@localhost:5432/topology_db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================================================
# Database Models
# ============================================================================

class Host(Base):
    __tablename__ = "hosts"

    id = Column(Integer, primary_key=True)
    ip_address = Column(String(15), unique=True, index=True)
    mac_address = Column(String(17), nullable=True)
    hostname = Column(String(255), nullable=True)
    device_type = Column(String(50), nullable=True)
    glyph = Column(String(10), nullable=True)
    is_gateway = Column(Boolean, default=False)
    is_self = Column(Boolean, default=False)
    online = Column(Boolean, default=True)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True)
    scan_id = Column(String(50), unique=True, index=True)
    subnet = Column(String(30), nullable=True)
    gateway_ip = Column(String(15), nullable=True)
    self_ip = Column(String(15), nullable=True)
    total_hosts = Column(Integer, default=0)
    online_hosts = Column(Integer, default=0)
    scanned_at = Column(DateTime, default=datetime.utcnow)

class ActionHistory(Base):
    __tablename__ = "action_history"

    id = Column(Integer, primary_key=True)
    host_ip = Column(String(15), index=True)
    action_type = Column(String(50))
    action_data = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ============================================================================
# Pydantic Schemas
# ============================================================================

class HostSchema(BaseModel):
    ip: str
    mac: Optional[str] = None
    name: Optional[str] = None
    isSelf: bool = False
    isGateway: bool = False
    online: bool = True
    device_type: Optional[str] = None
    glyph: Optional[str] = None

class DiscoveryResponse(BaseModel):
    self: str
    gateway: Optional[str] = None
    subnet: str
    count: int
    hosts: List[HostSchema]

class ActionRequest(BaseModel):
    ip: str
    mac: Optional[str] = None
    type: str
    text: Optional[str] = None
    via: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None

# ============================================================================
# Network Discovery Functions (ported from server.js)
# ============================================================================

async def run_command(cmd: str) -> str:
    """Execute shell command and return output"""
    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )
        stdout, _ = await process.communicate()
        return stdout.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Command error: {e}")
        return ""

async def get_active_network():
    """Find active network interface (the one carrying default route)"""
    try:
        # Use ip route show to get default route
        output = await run_command("ip route show")

        for line in output.split('\n'):
            match = re.match(r'default via (\S+) dev (\S+)', line)
            if match:
                gateway, interface = match.groups()
                # Get the IP of this interface
                ip_output = await run_command(f"hostname -I")
                ips = ip_output.strip().split()
                if ips:
                    return {"gateway": gateway, "self": ips[0], "interface": interface}

        # Fallback: get first non-loopback IPv4
        output = await run_command("hostname -I")
        ips = output.strip().split()
        if ips:
            return {"gateway": None, "self": ips[0], "interface": None}

        return None
    except Exception as e:
        print(f"Network discovery error: {e}")
        return None

async def ping_host(ip: str) -> bool:
    """Check if host is reachable"""
    try:
        output = await run_command(f"ping -c 1 -W 1 {ip}")
        return " 0% packet loss" in output or "1 received" in output
    except:
        return False

async def get_arp_table(subnet_base: str) -> List[dict]:
    """Get ARP table for discovered hosts"""
    try:
        output = await run_command("arp -a")
        rows = []

        for line in output.split('\n'):
            # Parse: ? (x.x.x.x) at xx:xx:xx:xx:xx:xx on eth0
            match = re.search(r'\((\d+\.\d+\.\d+\.\d+)\) at ([0-9a-fA-F:]{17})', line)
            if match:
                ip, mac = match.groups()
                if ip.startswith(subnet_base):
                    last_octet = int(ip.split('.')[-1])
                    if last_octet not in (0, 255):  # Skip network and broadcast
                        rows.append({"ip": ip, "mac": mac.lower()})

        return rows
    except Exception as e:
        print(f"ARP table error: {e}")
        return []

async def reverse_dns(ip: str) -> Optional[str]:
    """Get hostname from IP"""
    try:
        name = socket.getfqdn(ip)
        if name != ip:
            return name
        return None
    except:
        return None

def get_device_glyph(hostname: str, is_gateway: bool, is_self: bool) -> str:
    """Determine device emoji based on hostname"""
    if is_gateway:
        return "🌐"
    if is_self:
        return "💻"

    name = (hostname or "").lower()

    if re.search(r"router|gw|gateway|switch", name):
        return "🌐"
    elif re.search(r"phone|iphone|android|galaxy|mobile", name):
        return "📱"
    elif re.search(r"tv|cast|roku|appletv", name):
        return "📺"
    elif re.search(r"print", name):
        return "🖨️"
    elif re.search(r"nas|synology|server|srv|esxi|vmware", name):
        return "🗄️"
    else:
        return "🖥️"

async def discover_network(db: Session):
    """Discover all devices on network"""
    net = await get_active_network()

    if not net or not net.get("self"):
        return {"error": "No active network interface found"}

    self_ip = net["self"]
    gateway_ip = net.get("gateway")
    subnet_base = ".".join(self_ip.split(".")[:3])

    # Ping sweep to populate ARP cache
    print(f"Scanning subnet: {subnet_base}.0/24")
    for i in range(1, 255):
        ip = f"{subnet_base}.{i}"
        asyncio.create_task(ping_host(ip))

    await asyncio.sleep(2)  # Wait for ping sweep to complete

    # Get ARP table
    arp_hosts = await get_arp_table(subnet_base)
    hosts = []

    for host_data in arp_hosts:
        ip = host_data["ip"]
        mac = host_data.get("mac", "")
        name = await reverse_dns(ip)
        is_self = ip == self_ip
        is_gateway = ip == gateway_ip if gateway_ip else False

        online = await ping_host(ip)

        # Save to database
        existing = db.query(Host).filter(Host.ip_address == ip).first()
        if existing:
            existing.mac_address = mac
            existing.hostname = name
            existing.online = online
            existing.last_seen = datetime.utcnow()
            existing.is_gateway = is_gateway
            existing.is_self = is_self
        else:
            db_host = Host(
                ip_address=ip,
                mac_address=mac,
                hostname=name,
                is_gateway=is_gateway,
                is_self=is_self,
                online=online
            )
            db.add(db_host)

        glyph = get_device_glyph(name, is_gateway, is_self)

        hosts.append(HostSchema(
            ip=ip,
            mac=mac,
            name=name,
            isSelf=is_self,
            isGateway=is_gateway,
            online=online,
            glyph=glyph
        ))

    db.commit()

    # Sort by last octet
    hosts.sort(key=lambda h: int(h.ip.split('.')[-1]))

    return DiscoveryResponse(
        self=self_ip,
        gateway=gateway_ip,
        subnet=f"{subnet_base}.0/24",
        count=len(hosts),
        hosts=hosts
    )

async def send_message_to_agent(ip: str, text: str, from_host: str = "topology-server") -> dict:
    """Send message to topology-agent running on target machine"""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=1.5) as client:
            response = await client.post(
                f"http://{ip}:9911/message",
                json={"text": text, "from": from_host},
                timeout=1.5
            )
            if response.status_code == 200:
                return {"ok": True, "via": "agent", "body": response.json()}
            else:
                return {"ok": False, "error": "Agent returned error"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ============================================================================
# FastAPI Application
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Topology Backend Starting...")
    yield
    print("🛑 Topology Backend Shutting Down...")

app = FastAPI(
    title="Live System Topology API",
    description="Network discovery and host management system",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Topology Backend",
        "version": "1.0.0"
    }

@app.get("/api/hosts")
async def get_hosts(db: Session = Depends(get_db)):
    """Discover and return all hosts on the network"""
    try:
        result = await discover_network(db)
        return result
    except Exception as e:
        print(f"Discovery error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/action")
async def execute_action(action: ActionRequest, db: Session = Depends(get_db)):
    """Execute action on target host (message, ping, wake)"""
    try:
        if action.type == "message":
            result = await send_message_to_agent(
                action.ip,
                action.text or "Hi",
                "topology-server"
            )
        elif action.type == "ping":
            online = await ping_host(action.ip)
            result = {"ok": online, "via": "ping"}
        else:
            raise HTTPException(status_code=400, detail="Unknown action type")

        # Log action
        history = ActionHistory(
            host_ip=action.ip,
            action_type=action.type,
            action_data=action.dict(),
            result=result
        )
        db.add(history)
        db.commit()

        return result
    except Exception as e:
        print(f"Action error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_history(db: Session = Depends(get_db)):
    """Get action history"""
    try:
        history = db.query(ActionHistory).order_by(ActionHistory.executed_at.desc()).limit(100).all()
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/topology")
async def get_topology():
    """Return the host's Docker topology as a Machine -> Container -> Image graph.

    Reads the real Docker daemon (via the mounted /var/run/docker.sock) and
    builds three tiers of nodes plus the edges that link them.
    """
    try:
        import docker
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="docker SDK not installed — rebuild the backend image (docker compose up -d --build backend)",
        )

    try:
        client = docker.from_env()
        info = client.info()

        machine = {
            "id": "machine",
            "name": info.get("Name") or "docker-host",
            "os": info.get("OperatingSystem") or "",
            "containers": info.get("Containers", 0),
            "images": info.get("Images", 0),
            "ncpu": info.get("NCPU"),
            "mem": info.get("MemTotal"),
        }

        containers = []
        images = {}
        edges = []

        for c in client.containers.list(all=True):
            cid = "c-" + c.id[:12]

            # Resolve the image this container runs from
            try:
                img = c.image
                tags = img.tags or []
                img_name = tags[0] if tags else img.short_id.replace("sha256:", "")[:12]
                iid = "img-" + img.id.replace("sha256:", "")[:12]
                img_size = img.attrs.get("Size")
            except Exception:
                img_name, iid, tags, img_size = "<unknown>", "img-unknown", [], None

            # Published host ports
            ports = []
            try:
                pmap = (c.attrs.get("NetworkSettings", {}) or {}).get("Ports") or {}
                for container_port, bindings in pmap.items():
                    for b in (bindings or []):
                        ports.append(f"{b.get('HostPort')}->{container_port}")
            except Exception:
                pass

            containers.append({
                "id": cid,
                "name": c.name,
                "status": c.status,          # running / exited / created / paused ...
                "image": img_name,
                "ports": ", ".join(sorted(set(ports)))[:60],
            })
            edges.append({"from": "machine", "to": cid, "kind": "runs"})

            if iid not in images:
                images[iid] = {"id": iid, "name": img_name, "size": img_size, "tags": tags}
            edges.append({"from": cid, "to": iid, "kind": "image"})

        return {
            "machine": machine,
            "containers": containers,
            "images": list(images.values()),
            "edges": edges,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Topology error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hosts/{ip}")
async def get_host_details(ip: str, db: Session = Depends(get_db)):
    """Get details for a specific host"""
    try:
        host = db.query(Host).filter(Host.ip_address == ip).first()
        if not host:
            raise HTTPException(status_code=404, detail="Host not found")
        return host
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
