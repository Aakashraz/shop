import redis
from django.conf import settings
from .models import Product


# connect to Redis database (like opening you notebook)
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

class Recommender:
    def get_product_key(self, id):
        return f'product:{id}:purchased_with'   # Generates a unique Redis key for each product.

    def product_bought(self, products):
        product_ids = [p.id for p in products]  # This grabs just the numeric IDs for efficiency.
        for product_id in product_ids:
            for with_id in product_ids:
                # get the other products bought with each product
                if product_id != with_id:
                    # increment score for product purchased together
                    r.zincrby(
                        self.get_product_key(product_id), 1, with_id
                    )

    def suggest_product_for(self, products, max_results=6):
        product_ids = [p.id for p in products]
        if len(products) == 1:
            # only 1 product
            suggestions = r.zrange(
                self.get_product_key(product_ids[0]), 0, -1, desc=True
            )[:max_results]
            # self.get_product_key(product_ids[0]) -> Get the Redis key (e.g., "product:2:purchased_with")
            # r.zrange(..., 0, -1, desc=True):
            # -> zrange = Get members from sorted set
            # -> 0, -1 = From start(0) to end(-1) = All members
            # -> desc=True = Descending order (highest score first)
            # Example result: [5,3,7,9,1,4] (product IDs sorted by score)
            # -> [:max_results]: Take only first 6 items, Result: [5,3,7,9,1,4]

        else:
            # generate a temporary key
            flat_ids = ''.join([str(id) for id in product_ids])
            # Combine all IDs into one string. Example: [2,3,5] -> "235"
            temp_key = f'temp_{flat_ids}'
            # Create a unique temporary key name. Result: "tmp_235"

            # multiple products, combine scores of all products
            # store the resulting sorted set in a temporary key
            keys = [self.get_product_key(id) for id in product_ids]
            r.zunionstore(temp_key, keys)

            # remove ids for the products the recommendation is for
            r.zrem(temp_key, *product_ids)
            # get the product ids by their score, descendant sort
            suggestions = r.zrange(
                temp_key, 0, -1, desc=True
            )[:max_results]
            # remove the temporary key
            r.delete(temp_key)

        suggested_products_ids = [int(id) for id in suggestions]
        # get suggested products and sort by order of appearance
        suggested_products = list(
            Product.objects.filter(id__in=suggested_products_ids)
        )
        suggested_products.sort(
            key=lambda x: suggested_products_ids.index(x.id)
        )

        return suggested_products



