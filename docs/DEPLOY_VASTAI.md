# Deploying the backend on Vast.ai

The backend is a single Docker container — CPU-only is fine (OpenCV + Tesseract,
no GPU needed), so pick the **cheapest CPU instance** (~$0.02–0.05/hr).

## Option A — Docker image (recommended)

1. Build & push the image from any machine with Docker (or use GitHub Actions —
   see below for a phone-only path):

   ```bash
   cd backend
   docker build -t YOURDOCKERHUB/electronics-scanner-api:latest .
   docker push YOURDOCKERHUB/electronics-scanner-api:latest
   ```

2. On [Vast.ai](https://vast.ai) → **Templates** → create a template:
   - **Image**: `YOURDOCKERHUB/electronics-scanner-api:latest`
   - **Launch mode**: Docker
   - **Expose port**: `8000`
   - **Environment**: `REQUIRE_PREMIUM=true`, and set your own
     `PREMIUM_DEV_TOKEN` (any random string — the app's demo Pro mode sends
     `premium-dev` by default, so change both together).

3. Rent a CPU instance with that template. Vast.ai maps container port 8000 to
   a public `IP:PORT` — shown on the instance card.

4. Verify from your phone browser: `http://IP:PORT/health` → `{"status":"ok"}`
   and `http://IP:PORT/docs` for the interactive API explorer.

## Option B — plain instance, no custom image

Rent any instance with a base Python/Ubuntu image, open a terminal (Vast.ai has
a web terminal — works from a phone), and run:

```bash
apt-get update && apt-get install -y git tesseract-ocr libgl1 libglib2.0-0
git clone https://github.com/engrjhon3-prog/AI-Electronics-Scan.git
cd AI-Electronics-Scan/backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

(Expose/forward port 8000 in the instance config.)

## Pointing the app at your server

The APK reads the backend URL from a build-time value. Set the GitHub repository
**variable** `API_BASE_URL` to `http://IP:PORT` (Settings → Secrets and
variables → Actions → Variables → New repository variable), then re-run the
**Build & Test** workflow. The new APK from the Releases page will talk to your
server.

> Note: the app allows plain HTTP (`usesCleartextTraffic`) because Vast.ai
> instances typically expose raw ports. For production, put the API behind a
> domain with HTTPS (e.g. Cloudflare Tunnel or a small VPS reverse proxy) and
> rebuild with the `https://` URL.

## Keeping costs down

- CPU-only inference: a $0.03/hr instance handles this API easily.
- Vast.ai bills while the instance runs; stop it when not needed.
- If you outgrow one box, the API is stateless — run two and round-robin.
