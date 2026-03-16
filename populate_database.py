import sqlite3
import random
import datetime

# Custom Fake Data Generators
def get_random_name():
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
    last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def get_random_email(name):
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "example.com"]
    clean_name = name.lower().replace(" ", ".")
    return f"{clean_name}{random.randint(1, 999)}@{random.choice(domains)}"

def get_random_phone():
    return f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

def get_random_address():
    streets = ["Main St", "High St", "Broadway", "Elm St", "Maple Ave", "Oak St", "Washington St", "Park Ave", "Lake View", "Hill St"]
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
    states = ["NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "CA"]
    return f"{random.randint(1, 999)} {random.choice(streets)}, {random.choice(cities)}, {random.choice(states)} {random.randint(10000, 99999)}"

def get_random_date_this_year():
    start_date = datetime.date(2025, 1, 1) # Assuming current year context or nearby
    end_date = datetime.date.today()
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    if days_between_dates < 1:
        days_between_dates = 1
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + datetime.timedelta(days=random_number_of_days)


def populate_database():
    conn = sqlite3.connect('pet_store.db')
    cursor = conn.cursor()

    # Generate Customers
    customers = []
    # Use a set to ensure unique emails
    existing_emails = set()
    
    while len(customers) < 50:
        name = get_random_name()
        email = get_random_email(name)
        if email in existing_emails:
            continue
        existing_emails.add(email)
        phone = get_random_phone()
        address = get_random_address()
        customers.append((name, email, phone, address))

    cursor.executemany('INSERT INTO customers (name, email, phone, address) VALUES (?, ?, ?, ?)', customers)
    print("Inserted 50 customers.")

    # Generate Products
    products = []
    categories = ['Pet', 'Accessory', 'Food', 'Toy', 'Health']
    
    # Predefined product names for better realism
    product_names = {
        'Pet': ['Golden Retriever Puppy', 'Siamese Kitten', 'Hamster', 'Parrot', 'Goldfish', 'Rabbit', 'Turtle', 'Guinea Pig'],
        'Accessory': ['Leash', 'Collar', 'Pet Bed', 'Aquarium', 'Bird Cage', 'Hamster Wheel', 'Cat Tree', 'Dog House'],
        'Food': ['Dog Food 10kg', 'Cat Food 5kg', 'Bird Seed', 'Fish Flakes', 'Hamster Mix', 'Rabbit Pellets'],
        'Toy': ['Squeaky Bone', 'Feather Wand', 'Laser Pointer', 'Chew Toy', 'Ball', 'Frisbee'],
        'Health': ['Flea Collar', 'Shampoo', 'Vitamins', 'Brush', 'Nail Clippers']
    }

    for _ in range(20):
        category = random.choice(categories)
        name = random.choice(product_names[category])
        # Add a random suffix to avoid duplicates if needed, or just allow common names
        price = round(random.uniform(5.0, 150.0), 2)
        stock = random.randint(0, 100)
        description = f"High quality {name} for your beloved pet."
        products.append((name, category, price, stock, description))

    cursor.executemany('INSERT INTO products (name, category, price, stock, description) VALUES (?, ?, ?, ?, ?)', products)
    print("Inserted 20 products.")

    # Generate Bills and Bill Items
    cursor.execute('SELECT id FROM customers')
    customer_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute('SELECT id, price FROM products')
    product_data = cursor.fetchall() # list of (id, price)

    if not customer_ids or not product_data:
        print("Error: Not enough customers or products to generate bills.")
        return

    for _ in range(30):
        customer_id = random.choice(customer_ids)
        date = get_random_date_this_year()
        
        # Create bill first to get ID
        cursor.execute('INSERT INTO bills (customer_id, date, total_amount) VALUES (?, ?, ?)', (customer_id, date.isoformat(), 0))
        bill_id = cursor.lastrowid

        total_amount = 0
        num_items = random.randint(1, 5)
        
        for _ in range(num_items):
            product_id, price = random.choice(product_data)
            quantity = random.randint(1, 5)
            subtotal = price * quantity
            total_amount += subtotal
            
            cursor.execute('INSERT INTO bill_items (bill_id, product_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)',
                           (bill_id, product_id, quantity, price, subtotal))

        # Update total amount for the bill
        cursor.execute('UPDATE bills SET total_amount = ? WHERE id = ?', (total_amount, bill_id))

    print("Inserted 30 bills with items.")

    conn.commit()
    conn.close()
    print("Database populated successfully.")

if __name__ == '__main__':
    populate_database()
