import os
from flask import Flask, request, jsonify
from ariadne import (
    load_schema_from_path,
    make_executable_schema,
    graphql_sync,
    snake_case_fallback_resolvers,
    ObjectType,
)
from ariadne.explorer import ExplorerGraphiQL

import resolvers

app = Flask(__name__)

# Load schema
type_defs = load_schema_from_path(
    os.path.join(os.path.dirname(__file__), "schema.graphql")
)

# Setup Query and Mutation types
query = ObjectType("Query")
mutation = ObjectType("Mutation")
bill = ObjectType("Bill")
bill_item = ObjectType("BillItem")

# Bind Queries
query.set_field("customers", resolvers.resolve_customers)
query.set_field("customer", resolvers.resolve_customer)
query.set_field("products", resolvers.resolve_products)
query.set_field("product", resolvers.resolve_product)
query.set_field("bills", resolvers.resolve_bills)
query.set_field("bill", resolvers.resolve_bill)

# Bind nested relations for Bills
bill.set_field("customer", resolvers.resolve_bill_customer)
bill.set_field("items", resolvers.resolve_bill_items)
bill_item.set_field("product", resolvers.resolve_bill_item_product)

# Bind Mutations
mutation.set_field("createCustomer", resolvers.resolve_create_customer)
mutation.set_field("updateCustomer", resolvers.resolve_update_customer)
mutation.set_field("deleteCustomer", resolvers.resolve_delete_customer)
mutation.set_field("createProduct", resolvers.resolve_create_product)
mutation.set_field("updateProduct", resolvers.resolve_update_product)
mutation.set_field("deleteProduct", resolvers.resolve_delete_product)
mutation.set_field("createBill", resolvers.resolve_create_bill)

# Create executable schema
schema = make_executable_schema(
    type_defs, query, mutation, bill, bill_item, snake_case_fallback_resolvers
)

# GraphiQL explorer
explorer_html = ExplorerGraphiQL().html(None)


@app.route("/graphql", methods=["GET"])
def graphql_playground():
    # Return GraphiQL UI on GET request
    return explorer_html, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    # Execute GraphQL query
    data = request.get_json()

    success, result = graphql_sync(schema, data, context_value=request, debug=app.debug)

    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    app.run(debug=True, port=5001)
