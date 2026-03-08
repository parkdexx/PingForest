# 🌲 PingForest

**PingForest** is an intuitive, hierarchical network monitoring tool designed to check asset availability (Ping, Port) effortlessly. It provides real-time visibility into your network infrastructure by periodically checking device availability and service status in a beautiful UI.

---

### ✨ Key Features

1. **Intuitive Tree-based Management**
   - Organize and group your network assets logically using folders (locations/departments) and nodes (servers/PCs).
2. **Real-time Monitoring & Status Checking**
   - **ICMP Ping**: Monitor network connectivity and latency response times.
   - **TCP Port**: Verify availability of specific services (HTTP, DB, SSH, etc.).
3. **Customizable Dashboard Mode**
   - A dedicated fullscreen-ready dashboard to oversee critical infrastructure at a glance.
   - Customize each node's tile with specific colors and icons for high visibility.
4. **Data Import/Export & Logging**
   - Backup or restore your entire tree hierarchy using JSON import/export functions.
   - Export detailed network connection logs to text files (`.txt`) for troubleshooting and record-keeping.

---

### 🚀 Getting Started

#### 1. Prerequisites & Installation
Ensure you have Python installed, then set up the environment:
```bash
# Create and activate virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Running the Application
```bash
python src/main.py
```

#### 3. How to Use
- **Adding Nodes**: Right-click on the left tree panel to add folders or devices.
- **Configuration**: Use the right detailing panel to input IP addresses, target ports, and customize dashboard appearances. Click "Save".
- **Dashboard**: Click the "Dashboard" button at the bottom left to view the status overview.
- **Exporting Logs**: Select a node with connection issues and click "Export" in the log panel to save a report.
