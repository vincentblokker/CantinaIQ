# Deploy — CantinaIQ dashboard to Hetzner

The dashboard is a static Vite + React SPA. The whole production bundle is
1.1 MB (HTML + minified JS + CSS + six JSON exports). No backend, no
database, no runtime — a plain webserver is enough.

This directory contains everything you need to host it.

```text
deploy/
├── DEPLOY.md              ← you are here
├── package.sh             ← rebuilds dashboard + produces a tarball
├── nginx.conf.example     ← drop-in nginx server block
└── Caddyfile.example      ← drop-in Caddyfile (recommended if Caddy is already on the box)
```

---

## Hard constraint: a dedicated (sub)domain

The dashboard fetches data from `/data/*.json` and JS/CSS from `/assets/*`
— both **absolute** from the host root. It cannot be served from a subpath
like `example.com/cantinaiq/` without a code change.

Pick a subdomain:

- `cantinaiq.vincentblokker.nl`
- `cantinaiq.clubduty.nl`
- `wine.vincentblokker.com`
- (or whatever fits your existing DNS setup)

Point the A record at the Hetzner box. Wait for DNS propagation (`dig
cantinaiq.example.nl` should resolve to the server IP).

---

## Option A — Caddy (recommended if Caddy already runs ClubDuty)

Caddy gives you automatic HTTPS via Let's Encrypt with one directive.

1. Copy the dashboard to the server:
   ```bash
   # from the repo root, on your laptop:
   tar -czf cantinaiq-dashboard.tar.gz -C dashboard/dist .
   scp cantinaiq-dashboard.tar.gz user@hetzner:/tmp/
   ```

2. On the server, extract to a serving directory:
   ```bash
   sudo mkdir -p /var/www/cantinaiq
   sudo tar -xzf /tmp/cantinaiq-dashboard.tar.gz -C /var/www/cantinaiq
   sudo chown -R caddy:caddy /var/www/cantinaiq
   ```

3. Add to the Caddyfile (see `Caddyfile.example` for the snippet):
   ```caddyfile
   cantinaiq.example.nl {
       root * /var/www/cantinaiq
       encode gzip
       try_files {path} /index.html
       file_server
   }
   ```

4. Reload:
   ```bash
   sudo caddy reload --config /etc/caddy/Caddyfile
   ```

That's it. Caddy fetches a cert automatically. Open
`https://cantinaiq.example.nl`.

---

## Option B — nginx

If the Hetzner box runs nginx (probably the case for ClubDuty), drop in a
server block from `nginx.conf.example`. You'll need to add TLS yourself —
either with Certbot or by sitting nginx behind a reverse proxy that
terminates TLS.

1. Same `tar` + `scp` + extract as above (use `/var/www/cantinaiq`).

2. Add an nginx vhost (`/etc/nginx/sites-available/cantinaiq.conf`):

   ```nginx
   server {
       listen 80;
       listen [::]:80;
       server_name cantinaiq.example.nl;

       root /var/www/cantinaiq;
       index index.html;

       # SPA fallback — React Router needs this for /regions, /matrix, /producers
       location / {
           try_files $uri $uri/ /index.html;
       }

       # Long cache for hashed assets, short for HTML
       location /assets/ {
           expires 1y;
           add_header Cache-Control "public, immutable";
       }
       location ~* \.json$ {
           expires 1h;
           add_header Cache-Control "public";
       }

       gzip on;
       gzip_types text/css application/javascript application/json;
   }
   ```

3. Enable + reload:
   ```bash
   sudo ln -s /etc/nginx/sites-available/cantinaiq.conf /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx
   ```

4. Get a TLS certificate:
   ```bash
   sudo certbot --nginx -d cantinaiq.example.nl
   ```

---

## Option C — Docker (if you prefer containers)

A two-line Dockerfile gives you a self-contained nginx image:

```dockerfile
FROM nginx:alpine
COPY dist /usr/share/nginx/html
COPY deploy/nginx.conf.example /etc/nginx/conf.d/default.conf
```

Build and ship via your usual ClubDuty registry workflow.

---

## Updating after a pipeline rerun

When you rerun the supercharged pipeline (`uv run cantinaiq run all`),
the JSON exports in `supercharged/data/exports/` change. To push those
changes to the live dashboard:

```bash
# from the repo root on your laptop
./deploy/package.sh                         # rebuild + tarball
scp cantinaiq-dashboard.tar.gz user@hetzner:/tmp/
ssh user@hetzner '
    sudo tar -xzf /tmp/cantinaiq-dashboard.tar.gz \
        -C /var/www/cantinaiq --overwrite
'
```

No restart needed — nginx/Caddy picks up changed files on the next
request.

---

## Quick local sanity check before deploying

```bash
cd dashboard
npm run build
npx vite preview --port 4173      # serves dist/ exactly like a production server
open http://localhost:4173
```

If the matrix page renders 762 bubbles and the regions table populates,
the bundle is ready to ship.

---

## What ADA will see

- `https://cantinaiq.example.nl/` — Overview with 3 KPIs and top-5 producers
- `https://cantinaiq.example.nl/regions` — sortable regions table
- `https://cantinaiq.example.nl/producers` — segment-filterable producer list
- `https://cantinaiq.example.nl/matrix` — 762-bubble opportunity matrix

Open the matrix page; that is the artefact that lets a non-technical
evaluator see the entire ranking without reading the ranking.
