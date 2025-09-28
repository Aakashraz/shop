import redis
from django.conf import settings
from .models import Product


# connect to redis
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

class Recommender:
    def get_product_key(self, id):
        return f'product:{id}:purchased_with'   # Generates a unique Redis key for each product.

    def product_bought(self, products):
        product_ids = [p.id for p in products]  # This grabs jus the numeric IDs for efficiency.
        for product_id in product_ids:
            for with_id in product_ids:
                # get the other products bought with each product
                if product_id != with_id:
                    # increment score for product purchased together
                    r.zincrby(
                        self.get_product_key(product_id), 1, with_id
                    )
