# Northstar Store — Full-Stack E-Commerce (Parts 1, 2 & 3)

This project extends the supplied Part 1 Flask/SQLite catalogue. It adds secure account registration/login, per-user persistent carts, backend ownership checks, an Alembic database migration, structured JSON logs, Prometheus metrics and a provisioned Grafana dashboard.

## Requirements
- Python 3.10+
- Docker Desktop with Docker Compose (for Prometheus/Grafana)

## Run the app (Windows PowerShell)
```powershell
python -m venv venv
.env\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```
Open http://127.0.0.1:5000. The app creates the SQLite database and tables on first run and seeds the Part 1 product catalogue only when it is empty.

## Run the app (Linux/macOS)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Existing Part 1 database and migration
Keep your original `instance/shop.sqlite3` in place. Back it up first. The Alembic migration adds `users`, `carts`, and `cart_items`; it does not drop or rewrite `products`.
```bash
alembic upgrade head
```
The app also has an idempotent schema bootstrap for easy first-time local setup. For a migration demonstration, run Alembic against a copy of the original Part 1 database, then verify `SELECT COUNT(*) FROM products;` before and after.

## User flow
1. Visit `/register`, create an account (password minimum 8 characters).
2. Log in at `/login`.
3. Browse products and choose **Add to cart**; unauthenticated users are redirected to login.
4. Visit `/cart` to update quantities or remove items. Cart contents persist in SQLite.

Passwords are stored using Werkzeug's salted password hash. Flask-Login maintains the session. Cart queries always use the authenticated user's `user_id`; API endpoints do not accept a user/cart id from the browser. Prices are read from the server-side `products` table, never from client input. Quantity and stock are validated server-side.

## API endpoints
| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| GET | `/api/products` | No | Product catalogue/search/filter/sort |
| GET | `/api/products/<id>` | No | Product detail |
| POST | `/api/cart/items` | Yes | Add item (`product_id`, `quantity`) |
| GET | `/api/cart` | Yes | Current user's cart and server-calculated total |
| PATCH | `/api/cart/items/<product_id>` | Yes | Update quantity (`quantity`) |
| DELETE | `/api/cart/items/<product_id>` | Yes | Remove item |
| GET | `/metrics` | No | Prometheus metrics |

### Authorization test
Create two accounts, A and B. Add a product while logged in as A. Log out and sign in as B. `GET /api/cart` must return B's cart, not A's. Try `DELETE /api/cart/items/1` while signed in as B: it returns 404 if that product is not in B's cart. The API does not take a cart id or user id, preventing ID substitution. Repeat with browser dev tools/curl while logged in to show the backend enforcement.

## Logging and metrics
JSON logs are written to the terminal with UTC timestamp, level, message, request ID, HTTP method/path/status and duration. Failed logins are logged without username/password values. Passwords and session tokens are never logged.

Prometheus metrics include total HTTP requests by method/endpoint/status, request latency histogram, failed logins and cart operations. `/metrics` exposes the scrape endpoint.

## Start monitoring
Start the Flask app first, then in another terminal from the project root:
```bash
docker compose up -d
```
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (login `admin`, password `admin12345`)
- Dashboard: Dashboards → E-Commerce → Northstar E-Commerce Monitoring

The dashboard includes request volume, p95 latency, HTTP errors and cart operations. Interact with the website and refresh the dashboard. For a controlled failure, request `/api/products/999999` (404) or attempt an invalid cart quantity; observe the error count and JSON request log. Stop stack: `docker compose down`.

Prometheus scrape target is `host.docker.internal:5000`. If Docker on your system cannot resolve this host, adjust the target in `prometheus/prometheus.yml` to the host address reachable from the container.

## Architecture
Browser (Jinja/HTML/CSS/JavaScript) → Flask routes/API → Flask-Login identity → SQLite users/carts/cart_items/products. Request middleware records JSON logs and Prometheus metrics. Prometheus scrapes `/metrics`; Grafana queries Prometheus and displays the provisioned dashboard.

## Screenshots to capture for submission
Run the app and capture: (1) registration/login page, (2) populated cart page, (3) Grafana dashboard with visible request/cart metrics, (4) terminal JSON log after a controlled 404/invalid request. Screenshots are intentionally not fabricated; capture them on your computer after running the stack.

## Security notes
Set a strong `SECRET_KEY` environment variable for any shared deployment. Use HTTPS and `COOKIE_SECURE=1` behind HTTPS. This is a teaching/demo project; do not use the sample Grafana password outside a local environment.
