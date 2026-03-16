import sqlite3
import os

DATABASE = "../../pet_store.db"


def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), DATABASE)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


# --- Queries ---


def resolve_customers(_, info):
    conn = get_db_connection()
    customers = conn.execute("SELECT * FROM customers").fetchall()
    conn.close()
    return [dict(c) for c in customers]


def resolve_customer(_, info, id):
    conn = get_db_connection()
    customer = conn.execute("SELECT * FROM customers WHERE id = ?", (id,)).fetchone()
    conn.close()
    return dict(customer) if customer else None


def resolve_products(_, info):
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return [dict(p) for p in products]


def resolve_product(_, info, id):
    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (id,)).fetchone()
    conn.close()
    return dict(product) if product else None


def resolve_bills(_, info):
    conn = get_db_connection()
    bills = conn.execute("SELECT * FROM bills").fetchall()
    conn.close()
    return [dict(b) for b in bills]


def resolve_bill(_, info, id):
    conn = get_db_connection()
    bill = conn.execute("SELECT * FROM bills WHERE id = ?", (id,)).fetchone()
    conn.close()
    return dict(bill) if bill else None


# --- Relationships in Bill and BillItem ---


def resolve_bill_customer(bill, info):
    conn = get_db_connection()
    customer = conn.execute(
        "SELECT * FROM customers WHERE id = ?", (bill["customer_id"],)
    ).fetchone()
    conn.close()
    return dict(customer) if customer else None


def resolve_bill_items(bill, info):
    conn = get_db_connection()
    items = conn.execute(
        "SELECT * FROM bill_items WHERE bill_id = ?", (bill["id"],)
    ).fetchall()
    conn.close()
    return [dict(i) for i in items]


def resolve_bill_item_product(bill_item, info):
    conn = get_db_connection()
    product = conn.execute(
        "SELECT * FROM products WHERE id = ?", (bill_item["product_id"],)
    ).fetchone()
    conn.close()
    return dict(product) if product else None


# --- Mutations ---


def resolve_create_customer(_, info, name, email, phone=None, address=None):
    conn = get_db_connection()
    try:
        cur = conn.execute(
            "INSERT INTO customers (name, email, phone, address) VALUES (?, ?, ?, ?)",
            (name, email, phone, address),
        )
        conn.commit()
        customer_id = cur.lastrowid
        customer = conn.execute(
            "SELECT * FROM customers WHERE id = ?", (customer_id,)
        ).fetchone()
        return dict(customer)
    except sqlite3.IntegrityError:
        raise Exception("Email already exists")
    finally:
        conn.close()


def resolve_update_customer(
    _, info, id, name=None, email=None, phone=None, address=None
):
    conn = get_db_connection()
    customer = conn.execute("SELECT * FROM customers WHERE id = ?", (id,)).fetchone()
    if not customer:
        conn.close()
        raise Exception("Customer not found")

    new_name = name if name is not None else customer["name"]
    new_email = email if email is not None else customer["email"]
    new_phone = phone if phone is not None else customer["phone"]
    new_address = address if address is not None else customer["address"]

    try:
        conn.execute(
            "UPDATE customers SET name = ?, email = ?, phone = ?, address = ? WHERE id = ?",
            (new_name, new_email, new_phone, new_address, id),
        )
        conn.commit()
        updated_customer = conn.execute(
            "SELECT * FROM customers WHERE id = ?", (id,)
        ).fetchone()
        return dict(updated_customer)
    except sqlite3.IntegrityError:
        raise Exception("Email already exists")
    finally:
        conn.close()


def resolve_delete_customer(_, info, id):
    conn = get_db_connection()
    customer = conn.execute("SELECT * FROM customers WHERE id = ?", (id,)).fetchone()
    if not customer:
        conn.close()
        return False

    conn.execute("DELETE FROM customers WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return True


def resolve_create_product(_, info, name, category, price, stock=0, description=None):
    conn = get_db_connection()
    cur = conn.execute(
        "INSERT INTO products (name, category, price, stock, description) VALUES (?, ?, ?, ?, ?)",
        (name, category, price, stock, description),
    )
    conn.commit()
    product_id = cur.lastrowid
    product = conn.execute(
        "SELECT * FROM products WHERE id = ?", (product_id,)
    ).fetchone()
    conn.close()
    return dict(product)


def resolve_update_product(
    _, info, id, name=None, category=None, price=None, stock=None, description=None
):
    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (id,)).fetchone()
    if not product:
        conn.close()
        raise Exception("Product not found")

    new_name = name if name is not None else product["name"]
    new_category = category if category is not None else product["category"]
    new_price = price if price is not None else product["price"]
    new_stock = stock if stock is not None else product["stock"]
    new_description = description if description is not None else product["description"]

    conn.execute(
        "UPDATE products SET name = ?, category = ?, price = ?, stock = ?, description = ? WHERE id = ?",
        (new_name, new_category, new_price, new_stock, new_description, id),
    )
    conn.commit()
    updated_product = conn.execute(
        "SELECT * FROM products WHERE id = ?", (id,)
    ).fetchone()
    conn.close()
    return dict(updated_product)


def resolve_delete_product(_, info, id):
    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (id,)).fetchone()
    if not product:
        conn.close()
        return False

    conn.execute("DELETE FROM products WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return True


def resolve_create_bill(_, info, customer_id, items):
    if not items:
        raise Exception("Bill must have at least one item")

    conn = get_db_connection()
    try:
        total_amount = 0
        bill_items_data = []  # (product_id, quantity, unit_price, subtotal)

        for item in items:
            product_id = item["product_id"]
            quantity = item["quantity"]

            product_row = conn.execute(
                "SELECT price FROM products WHERE id = ?", (product_id,)
            ).fetchone()
            if not product_row:
                raise Exception(f"Product {product_id} not found")

            price = product_row["price"]
            subtotal = price * quantity
            total_amount += subtotal
            bill_items_data.append((product_id, quantity, price, subtotal))

        # Create Bill
        cur = conn.execute(
            "INSERT INTO bills (customer_id, total_amount) VALUES (?, ?)",
            (customer_id, total_amount),
        )
        bill_id = cur.lastrowid

        # Create Bill Items
        for item_data in bill_items_data:
            conn.execute(
                "INSERT INTO bill_items (bill_id, product_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)",
                (bill_id, item_data[0], item_data[1], item_data[2], item_data[3]),
            )

        conn.commit()
        bill = conn.execute("SELECT * FROM bills WHERE id = ?", (bill_id,)).fetchone()
        return dict(bill)
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
