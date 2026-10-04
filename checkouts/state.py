def cart_signature(items):
    """The cart details the customer approved in the checkout step."""
    return sorted(
        [
            [
                item["product"].id,
                item["color"].id,
                item["quantity"],
                str(item["final_price"]),
            ]
            for item in items
        ],
        key=lambda item: (item[0], item[1]),
    )
