#!/bin/bash

BASE_URL="http://127.0.0.1:5000/api/v1"

echo "Testing API at $BASE_URL"

# 1. Get Customers
echo -e "\n1. GET /customers"
curl -s "$BASE_URL/customers" | head -n 5

# 2. Create Customer
echo -e "\n\n2. POST /customers"
curl -s -X POST -H "Content-Type: application/json" \
     -d '{"name": "Test User", "email": "test@example.com", "phone": "555-0000"}' \
     "$BASE_URL/customers"

# 3. Get Products
echo -e "\n\n3. GET /products"
curl -s "$BASE_URL/products" | head -n 5

# 4. Create Product
echo -e "\n\n4. POST /products"
curl -s -X POST -H "Content-Type: application/json" \
     -d '{"name": "Test Product", "category": "Test", "price": 10.5, "stock": 100}' \
     "$BASE_URL/products"

# 5. Create Bill
echo -e "\n\n5. POST /bills"
# Need valid customer and product IDs. Assuming we just created customer (likely ID 51) and product (likely ID 21)
# But to be safe, we'll try to use hardcoded IDs 1 and 1 if they exist, or the ones we just made?
# Let's just try with ID 1 for now as the DB is populated.
curl -s -X POST -H "Content-Type: application/json" \
     -d '{"customer_id": 1, "items": [{"product_id": 1, "quantity": 2}]}' \
     "$BASE_URL/bills"

echo -e "\n\nDone."
