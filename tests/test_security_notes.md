# Manual acceptance tests
- Register A and B; passwords are never stored in plaintext (`password_hash` is a Werkzeug hash).
- A adds product 1; `/api/cart` shows it.
- B logs in; `/api/cart` is empty. B cannot see or delete A's cart item because all cart SQL is scoped to B's server-side authenticated ID.
- Try quantity 0, 100, and greater than stock: API rejects it.
- Submit a fabricated `price` field: it is ignored; totals use `products.price` from SQLite.
- Restart Flask: cart rows remain in SQLite.
- Request a missing product to create a 404 metric and log entry.
