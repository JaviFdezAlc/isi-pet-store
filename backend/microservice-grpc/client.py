import grpc
import pet_store_pb2
import pet_store_pb2_grpc


def run():
    # Connect to the gRPC server
    print("Connecting to gRPC server on localhost:5002...")
    with grpc.insecure_channel("localhost:5002") as channel:
        stub = pet_store_pb2_grpc.PetStoreServiceStub(channel)

        print("\n--- Listing All Customers ---")
        try:
            response = stub.GetCustomers(pet_store_pb2.Empty())
            for c in response.customers:
                print(f"[{c.id}] {c.name} - {c.email}")
        except grpc.RpcError as e:
            print(f"RPC Error: {e.details()}")

        print("\n--- Listing All Products ---")
        try:
            response = stub.GetProducts(pet_store_pb2.Empty())
            for p in response.products:
                print(f"[{p.id}] {p.name} (${p.price:.2f}) - Stock: {p.stock}")
        except grpc.RpcError as e:
            print(f"RPC Error: {e.details()}")

        print("\n--- Listing All Bills ---")
        try:
            response = stub.GetBills(pet_store_pb2.Empty())
            for b in response.bills:
                print(
                    f"Bill #{b.id} | Customer ID: {b.customer_id} | Total: ${b.total_amount:.2f}"
                )
                for item in b.items:
                    print(
                        f"  -> {item.quantity}x {item.product_name} @ ${item.unit_price:.2f} (Subtotal: ${item.subtotal:.2f})"
                    )
        except grpc.RpcError as e:
            print(f"RPC Error: {e.details()}")


if __name__ == "__main__":
    run()
