# Client-Server System for Intelligent Monitoring and Analysis of Server Applications

## Architecture

| Service | Description | Port |
|---|---|---|
| **agent** | Lightweight FastAPI service deployed on the monitored server. Collects CPU, RAM, Disk I/O, Network, Average load, and Docker container metrics via `psutil` and Docker SDK | `8200` |
| **collector** | Metrics polling service. Queries registered agents on a configurable interval and stores time series in TimescaleDB | `8001` |
| **analysis** | ML pipeline service. Runs Prophet forecasting → Isolation Forest anomaly detection → XGBoost severity classification, and LLM interpretation via Ollama | `8003` |
| **alerter** | Incident management service. Stores confirmed anomalies in PostgreSQL and sends Telegram notifications | `8002` |
| **frontend** | React SPA. Real-time metric charts, agent management, and incident log | `3000` |
| **timescaledb** | Time-series storage for raw metrics | `5433` |
| **postgresql** | Relational storage for incidents | `5432` |
| **ollama** | Local LLM runtime for anomaly interpretation | `11434` |

---

## Agent

Deploy on each server you want to monitor.

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `AGENT_ID` | `unknown-agent` | Unique identifier for this agent within the monitoring stack |
| `AGENT_HOST` | `localhost` | Hostname or IP address of the monitored server |
| `PORT` | `8200` | Port the agent REST API listens on |
| `API_V1_STR` | `/api/v1` | API route prefix |

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
```

---

## Monitoring Server

Runs all backend services, the ML pipeline, and the frontend.

### Configuration

### Monitoring server environment variables

| Variable | Default | Description |
|---|---|---|
| `DB_USER` | `postgres` | TimescaleDB username |
| `DB_PASSWORD` | `postgres` | TimescaleDB password |
| `DB_NAME` | `metrics` | Metrics database name |
| `DB_PORT` | `5433` | TimescaleDB external port |
| `POSTGRES_USER` | `postgres` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `postgres` | PostgreSQL password |
| `POSTGRES_DB` | `monitoring` | Incidents database name |
| `POSTGRES_PORT` | `5432` | PostgreSQL external port |
| `POLL_INTERVAL` | `10` | Agent polling interval in seconds |
| `AGENT_TIMEOUT` | `15` | Agent connection timeout in seconds |
| `OLLAMA_MODEL` | `gemma3:4b` | LLM model name for anomaly interpretation |
| `TELEGRAM_BOT_TOKEN` | – | Telegram bot token for notifications |
| `TELEGRAM_CHAT_ID` | – | Telegram chat ID for notifications |
| `COLLECTOR_PORT` | `8001` | Collector service external port |
| `ALERTER_PORT` | `8002` | Alerter service external port |
| `ANALYSIS_PORT` | `8003` | Analysis service external port |
| `FRONTEND_PORT` | `3000` | Frontend external port |

### Analysis service environment variables

| Variable | Default | Description |
|---|---|---|
| `ANALYSIS_INTERVAL` | `10` | Analysis cycle interval in seconds |
| `AGENTS_REFRESH_INTERVAL` | `60` | Agent list cache refresh interval in seconds |
| `ANOMALY_COOLDOWN` | `60` | Minimum interval between alerts for the same agent in seconds |
| `RETRAIN_INTERVAL_HOURS` | `23` | Automatic model retraining interval in hours |
| `TRAINING_WINDOW_HOURS` | `72` | Historical data window size for training in hours |
| `MIN_TRAINING_SAMPLES` | `13000` | Minimum number of records required to start training |
| `ANOMALY_THRESHOLD_WARNING` | `0.75` | Normalized score threshold for warning level |
| `ANOMALY_THRESHOLD_CRITICAL` | `0.85` | Normalized score threshold for critical level |
| `ISO_CONTAMINATION` | `0.01` | Expected anomaly fraction in the Isolation Forest training set |
| `MODELS_DIR` | `/app/models` | Path to the trained models directory inside the container |


> **Note:** `COLLECTOR_PORT` and `ALERTER_PORT` change only the external ports exposed on the host. Nginx communicates with services over the internal Docker network using fixed container addresses (`collector:8001`, `alerter:8002`), so `nginx.conf` does not need to be updated when changing these values.

### Run

```bash
docker compose up -d
```

On first start, `ollama-init` pulls the configured model before other services start. This may take a few minutes depending on your connection speed.

### Verify

```bash
curl http://localhost:8001/api/v1/health   # collector
curl http://localhost:8002/api/v1/health   # alerter
curl http://localhost:8003/health          # analysis
curl http://localhost:3000                 # frontend
```

### Register an agent

Once the monitoring stack is running, open `http://localhost:3000`, click **Add agent**, and enter the agent's URL (e.g. `http://192.168.1.100:8200`) and a display name.

The collector will start polling the agent immediately. The analysis service requires at least **13 000 samples** (~36 hours at a 10 s interval) before the ML models can be trained for the first time.

---

## Deployment commands

| Command | Description |
|---|---|
| `docker compose up -d` | Start the full stack in detached mode |
| `docker compose down` | Stop all services, preserve data volumes |
| `docker compose down -v` | Stop all services and remove all volumes |
| `docker compose ps` | Show status of all services |
| `docker compose restart <service>` | Restart a specific service |
| `docker compose logs -f <service>` | Stream logs of a specific service |
| `docker compose exec ollama ollama list` | List downloaded LLM models |
| `docker compose exec analysis rm -rf /app/models/<agent_id>` | Delete trained models to force retraining for a specific agent |