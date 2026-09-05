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

    def _get_key(self, product_id, color_id):
        return f"{product_id}:{color_id}"

    def add(
        self,
        product,
        color,
        quantity=1
    ):
        product_id = str(product.id)
        color_id = str(color.id)

        quantity = int(quantity)

        if not product.colors.filter(
            id=color.id
        ).exists():
            raise ValueError(
                "این رنگ برای این محصول موجود نیست."
            )

        key = self._get_key(
            product_id,
            color_id
        )

        if key not in self.cart:

            self.cart[key] = {
                "product_id": product.id,
                "color_id": color.id,
                "quantity": 0,
            }

        new_quantity = (
            self.cart[key]["quantity"]
            + quantity
        )

        if new_quantity > product.stock:
            raise ValueError(
                "موجودی محصول کافی نیست."
            )

        self.cart[key]["quantity"] = new_quantity

        self.save()

    def update(
        self,
        product_id,
        color_id,
        quantity
    ):

        product_id = str(product_id)
        color_id = str(color_id)

        key = self._get_key(
            product_id,
            color_id
        )

        if key not in self.cart:
            raise KeyError(
                "این محصول با این رنگ در سبد خرید وجود ندارد."
            )

        product = Product.objects.filter(
            id=product_id,
            is_active=True
        ).first()

        if not product:
            self.delete(
                product_id,
                color_id
            )
            return

        quantity = int(quantity)

        if quantity < 1:
            self.delete(
                product_id,
                color_id
            )
            return

        if quantity > product.stock:
            raise ValueError(
                "موجودی محصول کافی نیست."
            )

        self.cart[key]["quantity"] = quantity

        self.save()

    def delete(
        self,
        product_id,
        color_id
    ):

        key = self._get_key(
            str(product_id),
            str(color_id)
        )

        if key in self.cart:
            del self.cart[key]
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

        for key, item in self.cart.items():

            product = products.get(
                item["product_id"]
            )

            if not product or not product.is_active:
                continue

            color_id = item.get("color_id")

            if not color_id:
                continue

            color = product.colors.filter(
                id=color_id,
                is_active=True
            ).first()

            if not color:
                continue

            if not color:
                continue

            quantity = item["quantity"]

            yield {
                "product": product,
                "color": color,
                "quantity": quantity,
                "price": product.price,
                "final_price": product.final_price,
                "total": product.final_price * quantity,
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