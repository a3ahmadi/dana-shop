from products.models import Product


CART_SESSION_ID = "cart"


class Cart:

    def __init__(self, request):
        self.session = request.session

        self.cart = self.session.get(
            CART_SESSION_ID,
            {}
        )

    def save(self):
        self.session[CART_SESSION_ID] = self.cart
        self.session.modified = True

    def add(self, product, quantity=1):

        product_id = str(product.id)

        quantity = int(quantity)

        if product_id not in self.cart:
            self.cart[product_id] = {
                "product_id": product.id,
                "quantity": 0,
            }

        new_quantity = (
            self.cart[product_id]["quantity"]
            + quantity
        )

        if new_quantity > product.stock:
            raise ValueError(
                "موجودی محصول کافی نیست."
            )

        self.cart[product_id]["quantity"] = new_quantity

        self.save()

    def update(self, product_id, quantity):

        product_id = str(product_id)

        if product_id not in self.cart:
            raise KeyError(
                "محصول در سبد خرید وجود ندارد."
            )

        product = Product.objects.filter(
            id=product_id,
            is_active=True
        ).first()

        if not product:
            self.delete(product_id)
            return

        quantity = int(quantity)

        if quantity < 1:
            self.delete(product_id)
            return

        if quantity > product.stock:
            raise ValueError(
                "موجودی محصول کافی نیست."
            )

        self.cart[product_id]["quantity"] = quantity

        self.save()

    def delete(self, product_id):

        product_id = str(product_id)

        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):

        self.cart = {}

        self.save()

    def count(self):

        return sum(
            item["quantity"]
            for item in self.cart.values()
        )

    def __len__(self):

        return self.count()

    def __iter__(self):

        product_ids = [
            item["product_id"]
            for item in self.cart.values()
        ]

        products = Product.objects.in_bulk(
            product_ids
        )

        for product_id, item in self.cart.items():

            product = products.get(
                item["product_id"]
            )

            if not product or not product.is_active:
                continue

            quantity = item["quantity"]

            yield {
                "product": product,
                "quantity": quantity,
                "price": product.price,
                "final_price": product.final_price,
                "total": (
                    product.final_price * quantity
                ),
            }

    def total(self):

        return sum(
            item["total"]
            for item in self
        )

    def total_original_price(self):

        return sum(
            item["product"].price * item["quantity"]
            for item in self
        )

    def total_discount(self):

        return (
            self.total_original_price()
            - self.total()
        )