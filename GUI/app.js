const API_URL = 'http://127.0.0.1:5000/api/v1';

const app = {
    init: () => {
        // Initialize Theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        app.updateThemeIcon(savedTheme);

        app.showSection('customers');
    },

    toggleTheme: () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        app.updateThemeIcon(newTheme);
    },

    updateThemeIcon: (theme) => {
        const icon = document.querySelector('#theme-toggle .icon');
        icon.textContent = theme === 'dark' ? '☀️' : '🌙';
    },

    showSection: (sectionId) => {
        // Update tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.textContent.toLowerCase() === sectionId) {
                btn.classList.add('active');
            }
        });

        // Hide all sections
        document.querySelectorAll('.section').forEach(sec => sec.style.display = 'none');

        // Show target section
        document.getElementById(`${sectionId}-section`).style.display = 'block';

        // Load data
        if (sectionId === 'customers') app.fetchCustomers();
        if (sectionId === 'products') app.fetchProducts();
        if (sectionId === 'bills') app.fetchBills();
    },

    // --- Customers ---
    fetchCustomers: async () => {
        try {
            const res = await fetch(`${API_URL}/customers`);
            const data = await res.json();
            const tbody = document.querySelector('#customers-table tbody');
            tbody.innerHTML = data.map(c => `
                <tr>
                    <td>${c.id}</td>
                    <td>${c.name}</td>
                    <td>${c.email}</td>
                    <td>${c.phone}</td>
                    <td>${c.address}</td>
                    <td>
                        <button class="btn danger" onclick="app.deleteCustomer(${c.id})">Delete</button>
                    </td>
                </tr>
            `).join('');
        } catch (e) { console.error(e); alert('Error loading customers'); }
    },

    openCustomerModal: () => {
        app.openModal('Add Customer', `
            <div class="form-group">
                <label>Name</label>
                <input type="text" id="cust-name" required>
            </div>
            <div class="form-group">
                <label>Email</label>
                <input type="email" id="cust-email" required>
            </div>
            <div class="form-group">
                <label>Phone</label>
                <input type="text" id="cust-phone">
            </div>
            <div class="form-group">
                <label>Address</label>
                <input type="text" id="cust-address">
            </div>
        `, app.saveCustomer);
    },

    saveCustomer: async () => {
        const data = {
            name: document.getElementById('cust-name').value,
            email: document.getElementById('cust-email').value,
            phone: document.getElementById('cust-phone').value,
            address: document.getElementById('cust-address').value
        };

        try {
            const res = await fetch(`${API_URL}/customers`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (res.ok) {
                app.closeModal();
                app.fetchCustomers();
            } else {
                const err = await res.json();
                alert('Error: ' + err.error);
            }
        } catch (e) { console.error(e); alert('Error saving customer'); }
    },

    deleteCustomer: async (id) => {
        if (!confirm('Are you sure?')) return;
        await fetch(`${API_URL}/customers/${id}`, { method: 'DELETE' });
        app.fetchCustomers();
    },

    // --- Products ---
    fetchProducts: async () => {
        try {
            const res = await fetch(`${API_URL}/products`);
            const data = await res.json();
            const tbody = document.querySelector('#products-table tbody');
            tbody.innerHTML = data.map(p => `
                <tr>
                    <td>${p.id}</td>
                    <td>${p.name}</td>
                    <td>${p.category}</td>
                    <td>$${p.price.toFixed(2)}</td>
                    <td>${p.stock}</td>
                    <td>${p.description}</td>
                    <td>
                        <button class="btn danger" onclick="app.deleteProduct(${p.id})">Delete</button>
                    </td>
                </tr>
            `).join('');
        } catch (e) { console.error(e); alert('Error loading products'); }
    },

    openProductModal: () => {
        app.openModal('Add Product', `
            <div class="form-group">
                <label>Name</label>
                <input type="text" id="prod-name" required>
            </div>
            <div class="form-group">
                <label>Category</label>
                <select id="prod-category">
                    <option>Pet</option>
                    <option>Accessory</option>
                    <option>Food</option>
                    <option>Toy</option>
                    <option>Health</option>
                </select>
            </div>
            <div class="form-group">
                <label>Price</label>
                <input type="number" step="0.01" id="prod-price" required>
            </div>
            <div class="form-group">
                <label>Stock</label>
                <input type="number" id="prod-stock" value="0">
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea id="prod-desc"></textarea>
            </div>
        `, app.saveProduct);
    },

    saveProduct: async () => {
        const data = {
            name: document.getElementById('prod-name').value,
            category: document.getElementById('prod-category').value,
            price: parseFloat(document.getElementById('prod-price').value),
            stock: parseInt(document.getElementById('prod-stock').value),
            description: document.getElementById('prod-desc').value
        };

        try {
            const res = await fetch(`${API_URL}/products`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (res.ok) {
                app.closeModal();
                app.fetchProducts();
            } else {
                alert('Error saving product');
            }
        } catch (e) { console.error(e); }
    },

    deleteProduct: async (id) => {
        if (!confirm('Are you sure?')) return;
        await fetch(`${API_URL}/products/${id}`, { method: 'DELETE' });
        app.fetchProducts();
    },

    // --- Bills ---
    fetchBills: async () => {
        try {
            const res = await fetch(`${API_URL}/bills`);
            const data = await res.json();
            const tbody = document.querySelector('#bills-table tbody');
            tbody.innerHTML = data.map(b => `
                <tr>
                    <td>${b.id}</td>
                    <td>${b.customer_id}</td>
                    <td>${b.date}</td>
                    <td>$${b.total_amount.toFixed(2)}</td>
                    <td><button class="btn secondary" onclick="app.viewBillDetails(${b.id})">View Items</button></td>
                    <td>-</td>
                </tr>
            `).join('');
        } catch (e) { console.error(e); }
    },

    viewBillDetails: async (id) => {
        const res = await fetch(`${API_URL}/bills/${id}`);
        const data = await res.json();
        let itemsHtml = `<table style="width:100%"><tr><th>Product</th><th>Qty</th><th>Price</th><th>Subtotal</th></tr>`;
        data.items.forEach(item => {
            itemsHtml += `<tr>
                <td>${item.product_name || item.product_id}</td>
                <td>${item.quantity}</td>
                <td>$${item.unit_price}</td>
                <td>$${item.subtotal}</td>
            </tr>`;
        });
        itemsHtml += `</table><h3>Total: $${data.total_amount.toFixed(2)}</h3>`;
        app.openModal(`Bill #${id} Details`, itemsHtml, null); // No save button
        document.getElementById('modal-save-btn').style.display = 'none';
    },

    openBillModal: async () => {
        // Fetch customers and products for dropdowns
        const [custRes, prodRes] = await Promise.all([
            fetch(`${API_URL}/customers`),
            fetch(`${API_URL}/products`)
        ]);
        const customers = await custRes.json();
        const products = await prodRes.json();

        let custOptions = customers.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
        let prodOptions = products.map(p => `<option value="${p.id}">${p.name} ($${p.price})</option>`).join('');

        window.productsData = products; // Store for price lookup

        app.openModal('Create New Bill', `
            <div class="form-group">
                <label>Customer</label>
                <select id="bill-customer">${custOptions}</select>
            </div>
            <div id="bill-items-container">
                <label>Items</label>
                <div class="item-row">
                    <select class="bill-product">${prodOptions}</select>
                    <input type="number" class="bill-qty" value="1" min="1" style="width: 60px">
                    <button type="button" class="btn danger" onclick="this.parentElement.remove()">X</button>
                </div>
            </div>
            <button type="button" class="btn secondary" onclick="app.addBillItem('${prodOptions.replace(/"/g, '&quot;')}')">+ Add Item</button>
        `, app.saveBill);
    },

    addBillItem: (optionsHtml) => {
        const div = document.createElement('div');
        div.className = 'item-row';
        div.innerHTML = `
            <select class="bill-product">${optionsHtml}</select>
            <input type="number" class="bill-qty" value="1" min="1" style="width: 60px">
            <button type="button" class="btn danger" onclick="this.parentElement.remove()">X</button>
        `;
        document.getElementById('bill-items-container').appendChild(div);
    },

    saveBill: async () => {
        const customerId = document.getElementById('bill-customer').value;
        const items = [];
        document.querySelectorAll('.item-row').forEach(row => {
            const prodId = row.querySelector('.bill-product').value;
            const qty = row.querySelector('.bill-qty').value;
            items.push({ product_id: parseInt(prodId), quantity: parseInt(qty) });
        });

        if (items.length === 0) { alert('Add at least one item'); return; }

        try {
            const res = await fetch(`${API_URL}/bills`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ customer_id: parseInt(customerId), items: items })
            });
            if (res.ok) {
                app.closeModal();
                app.fetchBills();
            } else {
                const err = await res.json();
                alert('Error: ' + err.error);
            }
        } catch (e) { console.error(e); }
    },

    // --- Modal Utils ---
    openModal: (title, html, saveCallback) => {
        document.getElementById('modal-title').textContent = title;
        document.getElementById('modal-form').innerHTML = html;
        document.getElementById('modal').style.display = 'block';

        const saveBtn = document.getElementById('modal-save-btn');
        if (saveCallback) {
            saveBtn.style.display = 'inline-block';
            saveBtn.onclick = saveCallback;
        } else {
            saveBtn.style.display = 'none';
        }
    },

    closeModal: () => {
        document.getElementById('modal').style.display = 'none';
    }
};

window.onload = app.init;
