# Project Summary — `practica1-isi`

> **Purpose of this document:** Quick-reference for AI agents working on this codebase. It describes the project's purpose, architecture, file structure, data model, and API surface.

---

## 1. Overview

**Pet Store Manager** is a full-stack web application for managing a pet store's back-office data: customers, products, and purchase bills. It consists of:

- A **Python/Flask REST API** (backend) that talks to an **SQLite** database.
- A **vanilla HTML/CSS/JS single-page application** (frontend) served as static files.

The project is a university practice assignment (`practica1-isi`).

---

## 2. Tech Stack

| Layer      | Technology                           |
| ---------- | ------------------------------------ |
| Backend    | Python 3, Flask                      |
| Database   | SQLite 3 (`pet_store.db`)            |
| Frontend   | HTML5, Vanilla CSS, Vanilla JS       |
| Dev server | Flask built-in (`port 5000`)         |
| Runtime    | Python virtual environment (`venv/`) |

---

## 3. Project Structure

```
practica1-isi/
│
├── app.py                  # Flask REST API — main entry point
├── setup_database.py       # Creates the SQLite schema (run once)
├── populate_database.py    # Seeds the DB with fake data (50 customers, 20 products, 30 bills)
├── verify_api.sh           # Bash smoke-test script for the API (uses curl)
├── pet_store.db            # SQLite database file (generated, not source)
├── venv/                   # Python virtual environment (generated, not source)
│
└── GUI/                    # Static frontend (SPA)
    ├── index.html          # Shell HTML — tab layout + modal container
    ├── styles.css          # All CSS — CSS variables, dark/light mode, responsive layout
    └── app.js              # All JS — API calls, DOM manipulation, modal management
```

---

## 4. Database Schema

Four tables with the following relationships:

```
customers (id, name, email*, phone, address, created_at)
    │
    └──< bills (id, customer_id→customers, date, total_amount)
                │
                └──< bill_items (id, bill_id→bills, product_id→products,
                                  quantity, unit_price, subtotal)

products (id, name, category, price, stock, description)
```

> `*` `email` has a `UNIQUE` constraint.  
> Foreign keys: `bills.customer_id → customers.id`, `bill_items.bill_id → bills.id`, `bill_items.product_id → products.id`.

**Product categories:** `Pet`, `Accessory`, `Food`, `Toy`, `Health`.

---

## 5. REST API Reference

**Base URL:** `http://127.0.0.1:5000/api/v1`  
**CORS:** Enabled for all origins.  
**Content-Type:** `application/json` for request bodies.

### Customers

| Method | Endpoint          | Description                    | Required Body Fields       |
| ------ | ----------------- | ------------------------------ | -------------------------- |
| GET    | `/customers`      | List all customers             | —                          |
| GET    | `/customers/<id>` | Get a single customer          | —                          |
| POST   | `/customers`      | Create a customer              | `name`, `email`            |
| PUT    | `/customers/<id>` | Update a customer (partial ok) | any of the customer fields |
| DELETE | `/customers/<id>` | Delete a customer              | —                          |

### Products

| Method | Endpoint         | Description                   | Required Body Fields      |
| ------ | ---------------- | ----------------------------- | ------------------------- |
| GET    | `/products`      | List all products             | —                         |
| GET    | `/products/<id>` | Get a single product          | —                         |
| POST   | `/products`      | Create a product              | `name`, `price`           |
| PUT    | `/products/<id>` | Update a product (partial ok) | any of the product fields |
| DELETE | `/products/<id>` | Delete a product              | —                         |

### Bills

| Method | Endpoint      | Description                      | Required Body Fields                             |
| ------ | ------------- | -------------------------------- | ------------------------------------------------ |
| GET    | `/bills`      | List all bills                   | —                                                |
| GET    | `/bills/<id>` | Get a bill with its line items   | —                                                |
| POST   | `/bills`      | Create a bill (calculates total) | `customer_id`, `items: [{product_id, quantity}]` |

> Bills do **not** expose PUT or DELETE endpoints.

---

## 6. Backend Key Files

### `app.py`

- Single Flask application file.
- Helper functions: `get_db()`, `close_connection()`, `query_db()`.
- Standard error handlers for 400 and 404.
- Bill creation is the most complex endpoint: it validates all items, calculates the total, inserts into `bills` and `bill_items` in a single transaction with rollback on error.

### `setup_database.py`

- Run **once** to initialise the schema: `python setup_database.py`
- Uses `CREATE TABLE IF NOT EXISTS` — safe to re-run.

### `populate_database.py`

- Seeds with randomised fake data using only the standard library (`random`, `datetime`, `sqlite3`).
- Inserts: **50 customers** (unique emails enforced), **20 products**, **30 bills** (1–5 items each).
- Run **after** `setup_database.py`: `python populate_database.py`

### `verify_api.sh`

- Bash script to perform a quick smoke test of the running API.
- Covers: GET customers, POST customer, GET products, POST product, POST bill.
- Assumes the Flask server is already running.

---

## 7. Frontend — `GUI/`

The frontend is a **single-page application** with no build step or framework.

### `index.html`

- Tab-based navigation: **Customers**, **Products**, **Bills**.
- Each tab maps to a `<div class="section" id="*-section">` that is shown/hidden via JS.
- A single reusable modal (`#modal`) is used for all create/detail forms — its content is injected dynamically by `app.js`.

### `app.js`

Single global `app` object with methods grouped by domain:

| Group            | Key Methods                                                                             |
| ---------------- | --------------------------------------------------------------------------------------- |
| **Init / Theme** | `init()`, `toggleTheme()`, `updateThemeIcon()`                                          |
| **Navigation**   | `showSection(sectionId)`                                                                |
| **Customers**    | `fetchCustomers()`, `openCustomerModal()`, `saveCustomer()`, `deleteCustomer(id)`       |
| **Products**     | `fetchProducts()`, `openProductModal()`, `saveProduct()`, `deleteProduct(id)`           |
| **Bills**        | `fetchBills()`, `viewBillDetails(id)`, `openBillModal()`, `addBillItem()`, `saveBill()` |
| **Modal Utils**  | `openModal(title, html, saveCallback)`, `closeModal()`                                  |

Theme preference is persisted in `localStorage` (`key: 'theme'`, values: `'light'` | `'dark'`).  
API base URL is hardcoded at the top: `const API_URL = 'http://127.0.0.1:5000/api/v1'`.

### `styles.css`

- CSS custom properties (variables) on `:root` for light mode; overrides on `[data-theme="dark"]`.
- Smooth transitions on `background-color`, `color`, and `border-color` for theme switching.
- Max-width container: `1200px`.
- Responsive modal (`max-width: 90%`).

---

## 8. How to Run

```bash
# 1. Activate the virtual environment
source venv/bin/activate

# 2. (First time only) Create the database schema
python setup_database.py

# 3. (Optional) Seed with fake data
python populate_database.py

# 4. Start the Flask server
python app.py
# → Runs on http://127.0.0.1:5000

# 5. Open the frontend
open GUI/index.html   # macOS — or just open in any browser

# 6. (Optional) Smoke-test the API
bash verify_api.sh
```

---

## 9. Known Limitations & Notes for Agents

- **No authentication** — all endpoints are public.
- **No stock decrement** — bill creation reads stock for price but does not reduce it (commented-out code in `app.py` line 236).
- **Bills are immutable** — no PUT/DELETE on bills.
- **No UPDATE on bills** — to correct a bill, it must be recreated.
- **Frontend hardcodes the API URL** — if the backend port changes, update `API_URL` in `GUI/app.js`.
- **No `.gitignore`** — `venv/`, `pet_store.db`, and `.DS_Store` are committed (or at least present) in the working directory.
- **No tests** — only the manual `verify_api.sh` smoke-test exists.
- **No pagination** — all list endpoints return the full table contents.
