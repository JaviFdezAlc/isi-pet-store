from flask import Flask, jsonify, request, g
import sqlite3

app = Flask(__name__)
DATABASE = 'pet_store.db'
API_VERSION = '/api/v1'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# Error Handling
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

# CORS Support
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# --- Customers Endpoints ---

@app.route(f'{API_VERSION}/customers', methods=['GET'])
def get_customers():
    customers = query_db('SELECT * FROM customers')
    return jsonify([dict(ix) for ix in customers])

@app.route(f'{API_VERSION}/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = query_db('SELECT * FROM customers WHERE id = ?', [customer_id], one=True)
    if customer is None:
        return jsonify({'error': 'Customer not found'}), 404
    return jsonify(dict(customer))

@app.route(f'{API_VERSION}/customers', methods=['POST'])
def create_customer():
    if not request.json or not 'name' in request.json or not 'email' in request.json:
        return jsonify({'error': 'Invalid input, name and email are required'}), 400
    
    name = request.json['name']
    email = request.json['email']
    phone = request.json.get('phone', "")
    address = request.json.get('address', "")
    
    db = get_db()
    try:
        cur = db.execute('INSERT INTO customers (name, email, phone, address) VALUES (?, ?, ?, ?)',
                         (name, email, phone, address))
        db.commit()
        customer_id = cur.lastrowid
        cur.close()
        return jsonify({'id': customer_id, 'name': name, 'email': email, 'phone': phone, 'address': address}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already exists'}), 400

@app.route(f'{API_VERSION}/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    if not request.json:
        return jsonify({'error': 'Invalid input'}), 400
    
    customer = query_db('SELECT * FROM customers WHERE id = ?', [customer_id], one=True)
    if customer is None:
        return jsonify({'error': 'Customer not found'}), 404
        
    name = request.json.get('name', customer['name'])
    email = request.json.get('email', customer['email'])
    phone = request.json.get('phone', customer['phone'])
    address = request.json.get('address', customer['address'])
    
    db = get_db()
    try:
        db.execute('UPDATE customers SET name = ?, email = ?, phone = ?, address = ? WHERE id = ?',
                   (name, email, phone, address, customer_id))
        db.commit()
        return jsonify({'id': customer_id, 'name': name, 'email': email, 'phone': phone, 'address': address})
    except sqlite3.IntegrityError:
         return jsonify({'error': 'Email already exists'}), 400

@app.route(f'{API_VERSION}/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = query_db('SELECT * FROM customers WHERE id = ?', [customer_id], one=True)
    if customer is None:
        return jsonify({'error': 'Customer not found'}), 404
    
    db = get_db()
    db.execute('DELETE FROM customers WHERE id = ?', [customer_id])
    db.commit()
    return jsonify({'result': True})

# --- Products Endpoints ---

@app.route(f'{API_VERSION}/products', methods=['GET'])
def get_products():
    products = query_db('SELECT * FROM products')
    return jsonify([dict(ix) for ix in products])

@app.route(f'{API_VERSION}/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = query_db('SELECT * FROM products WHERE id = ?', [product_id], one=True)
    if product is None:
         return jsonify({'error': 'Product not found'}), 404
    return jsonify(dict(product))

@app.route(f'{API_VERSION}/products', methods=['POST'])
def create_product():
    if not request.json or not 'name' in request.json or not 'price' in request.json:
         return jsonify({'error': 'Invalid input, name and price are required'}), 400

    name = request.json['name']
    category = request.json.get('category', 'General')
    price = request.json['price']
    stock = request.json.get('stock', 0)
    description = request.json.get('description', "")

    db = get_db()
    cur = db.execute('INSERT INTO products (name, category, price, stock, description) VALUES (?, ?, ?, ?, ?)',
                     (name, category, price, stock, description))
    db.commit()
    product_id = cur.lastrowid
    cur.close()
    return jsonify({'id': product_id, 'name': name, 'category': category, 'price': price, 'stock': stock, 'description': description}), 201

@app.route(f'{API_VERSION}/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    if not request.json:
        return jsonify({'error': 'Invalid input'}), 400
    
    product = query_db('SELECT * FROM products WHERE id = ?', [product_id], one=True)
    if product is None:
        return jsonify({'error': 'Product not found'}), 404

    name = request.json.get('name', product['name'])
    category = request.json.get('category', product['category'])
    price = request.json.get('price', product['price'])
    stock = request.json.get('stock', product['stock'])
    description = request.json.get('description', product['description'])

    db = get_db()
    db.execute('UPDATE products SET name = ?, category = ?, price = ?, stock = ?, description = ? WHERE id = ?',
               (name, category, price, stock, description, product_id))
    db.commit()
    return jsonify({'id': product_id, 'name': name, 'category': category, 'price': price, 'stock': stock, 'description': description})

@app.route(f'{API_VERSION}/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = query_db('SELECT * FROM products WHERE id = ?', [product_id], one=True)
    if product is None:
        return jsonify({'error': 'Product not found'}), 404
        
    db = get_db()
    db.execute('DELETE FROM products WHERE id = ?', [product_id])
    db.commit()
    return jsonify({'result': True})

# --- Bills Endpoints ---

@app.route(f'{API_VERSION}/bills', methods=['GET'])
def get_bills():
    bills = query_db('SELECT * FROM bills')
    return jsonify([dict(ix) for ix in bills])

@app.route(f'{API_VERSION}/bills/<int:bill_id>', methods=['GET'])
def get_bill(bill_id):
    bill = query_db('SELECT * FROM bills WHERE id = ?', [bill_id], one=True)
    if bill is None:
        return jsonify({'error': 'Bill not found'}), 404
    
    # Join with products to get product name
    items = query_db('''
        SELECT bi.*, p.name as product_name 
        FROM bill_items bi
        JOIN products p ON bi.product_id = p.id
        WHERE bi.bill_id = ?
    ''', [bill_id])
    
    bill_dict = dict(bill)
    bill_dict['items'] = [dict(ix) for ix in items]
    
    return jsonify(bill_dict)

@app.route(f'{API_VERSION}/bills', methods=['POST'])
def create_bill():
    if not request.json or not 'customer_id' in request.json or not 'items' in request.json:
         return jsonify({'error': 'Invalid input, customer_id and items are required'}), 400

    customer_id = request.json['customer_id']
    items = request.json['items'] # List of {product_id, quantity}
    
    if not items:
         return jsonify({'error': 'Bill must have at least one item'}), 400

    db = get_db()
    try:
        # Start transaction logic implicit with sqlite3 context, but good to be careful
        
        # Calculate total and verify products
        total_amount = 0
        bill_items_data = [] # (product_id, quantity, unit_price, subtotal)
        
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity')
            
            if not product_id or not quantity:
                 return jsonify({'error': 'Invalid item format'}), 400
                 
            # Check product and stock
            product_row = db.execute('SELECT price, stock FROM products WHERE id = ?', (product_id,)).fetchone()
            if not product_row:
                return jsonify({'error': f'Product {product_id} not found'}), 400
            
            price = product_row[0]
            # stock = product_row[1] # Could check stock here
            
            subtotal = price * quantity
            total_amount += subtotal
            bill_items_data.append((product_id, quantity, price, subtotal))

        # Create Bill
        cur = db.execute('INSERT INTO bills (customer_id, total_amount) VALUES (?, ?)', (customer_id, total_amount))
        bill_id = cur.lastrowid
        
        # Create Bill Items
        for item_data in bill_items_data:
            db.execute('INSERT INTO bill_items (bill_id, product_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)',
                       (bill_id, item_data[0], item_data[1], item_data[2], item_data[3]))
        
        db.commit()
        return jsonify({'id': bill_id, 'customer_id': customer_id, 'total_amount': total_amount, 'item_count': len(items)}), 201

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
