"""""
   def get_restaurant(self, order: dict) -> list[Restaurant]:
        restaurants: list[Restaurant] = self.restaurant_service.get_all_restaurant()
        available_restaurant = defaultdict(lambda : defaultdict(dict))
        order_details = order.copy()
        can_be_place = []
        for restaurant in restaurants:
            for item in order_details.keys():
                if restaurant.is_item_available(item):
                    available_restaurant[restaurant]['orders'][item] = order_details[item]
                    can_be_place.append(item)

            if len(can_be_place) == len(order_details):
                available_restaurant[restaurant]['status']['all'] = True
            else:
                available_restaurant[restaurant]['status']['all'] = False

        all_orders = []
        partial_orders = []
        for restaurant in available_restaurant:
            if available_restaurant[restaurant]['status']['all']:
                all_orders.append((restaurant,available_restaurant[restaurant]['orders']))
            partial_orders.append((restaurant,available_restaurant[restaurant]['orders']))

        return all_orders

"""
