# Client-server system for intelligent monitoring and state analysis of server applications based on system metrics

## Architecture

| Service | Description | Port |
|---|---|---|
| **agent** | Lightweight FastAPI service deployed on monitored server. Collects CPU, RAM, Disk I/O, Network, Average load, and Docker containers metrics via `psutil` and Docker SDK | `8200` |
| **collector** | Central metrics polling service. Queries registered agents on a configurable interval and stores metrics in TimescaleDB | `8001` |
| **analysis** | ML pipeline service. Runs Prophet forecasting, Isolation Forest anomaly detection, XGBoost severity classification, and LLM interpretation via Ollama | `8003` |
| **alerter** | Incident management service. Stores confirmed anomalies in PostgreSQL and sends Telegram notifications | `8002` |
| **frontend** | React SPA. Real-time metric charts, agent management, and incident log | `3000` |
| **timescaledb** | Time-series storage for raw metrics | `5433` |
| **postgresql** | Relational storage for incidents and agent metadata | `5432` |
| **ollama** | Local LLM runtime for anomaly interpretation | `11434` |

---

## Agent

Deploy on each server you want to monitor.

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `AGENT_ID` | `unknown-agent` | Unique identifier for this agent, used as a key in the monitoring system |
| `AGENT_HOST` | `localhost` | Hostname or IP address of the monitored server, returned in `/host` response |
| `PORT` | `8000` | Port the agent listens on |

The agent mounts `/proc`, `/sys`, and `/var/run/docker.sock` from the host to access system-level metrics and Docker stats.

### agent/.env example

```env
AGENT_ID=production-server
AGENT_HOST=192.168.1.100
PORT=8200
```

### Run

```bash
cd agent
docker compose up -d
```

### Verify

```bash
curl http://localhost:8200/api/v1/health
curl http://localhost:8200/api/v1/host
curl http://localhost:8200/api/v1/metrics
```

---

## Monitoring Server

Runs all backend services, the ML pipeline, and the frontend.

### Configuration

The root `.env` file is used by Docker Compose only for variable substitution in `docker-compose.yaml`. Services receive their configuration as environment variables injected by Docker Compose via the `environment:` they do not read the root `.env` directly.

### .env example (root – Docker Compose variable substitution)

```env
# TimescaleDB – stores raw metric time series
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=metrics
DB_PORT=5433

# PostgreSQL – stores incidents and agent metadata
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=monitoring
POSTGRES_PORT=5432

# Collector
POLL_INTERVAL=10
AGENT_TIMEOUT=15

# Ollama
OLLAMA_MODEL=gemma3:4b

# Analysis
ANALYSIS_INTERVAL=10
AGENTS_REFRESH_INTERVAL=60
ANOMALY_COOLDOWN=60
RETRAIN_INTERVAL_HOURS=23
TRAINING_WINDOW_HOURS=72
MIN_TRAINING_SAMPLES=13000
ANOMALY_THRESHOLD_WARNING=0.80
ANOMALY_THRESHOLD_CRITICAL=0.90
ISO_CONTAMINATION=0.03

# Alerter
# Telegram notifications (optional — leave empty to disable)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Service ports (optional, defaults shown)
COLLECTOR_PORT=8001
ALERTER_PORT=8002
ANALYSIS_PORT=8003
FRONTEND_PORT=3000
```

> **Note:** `COLLECTOR_PORT` and `ALERTER_PORT` change only the external ports exposed on the host. Nginx communicates with services over the internal Docker network using fixed container addresses (`collector:8001`, `alerter:8002`), so `nginx.conf` does not need to be updated when changing these values.

### Run

```bash
docker compose up
```

On first start, `ollama-init` pulls the configured model before other services start. This may take a few minutes depending on your connection.

### Verify

```bash
curl http://localhost:8001/api/v1/health   # collector
curl http://localhost:8002/api/v1/health   # alerter
curl http://localhost:8003/health          # analysis
curl http://localhost:3000                 # frontend
```

### Register an agent

Once the monitoring stack is running, open `http://localhost:3000`, click **Add agent**, and enter the agent's URL (e.g. `http://192.168.1.100:8200`) and a display name.

The collector will start polling the agent immediately. The analysis service requires at least **13000 samples** (~36 hours at 10s interval) before the ML models can be trained for the first time.