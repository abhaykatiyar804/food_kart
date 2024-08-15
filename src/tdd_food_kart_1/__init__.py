import threading
import time

from tdd_food_kart_1.core.restaurant import Restaurant, SelectionStrategy, RestaurantStore, RestaurantService, \
    OrderStore, OrderService, OrderManager

print("This is main module")

def main():


    restaurant_store = RestaurantStore()
    restaurant_service = RestaurantService(restaurant_store)

    order_store = OrderStore()
    order_service = OrderService(order_store=order_store)
    order_manager = OrderManager(
    restaurant_service=restaurant_service, order_service=order_service
    )

    restaurant_service.register_restaurant(
    name="BurgerKing",
    menu={"king_burger": 10, "samosa_pizza": 20, "alu_pasta": 19},
    capacity=15,
    order_manager=order_manager,
    )
    restaurant_service.register_restaurant(
    name="Sarvana",
    menu={"bendi_macaroni": 12, "samosa_pizza": 25, "alu_pasta": 17},
    capacity=20,
    order_manager=order_manager,
    )

    restaurants: list[Restaurant] = restaurant_service.get_all_restaurant()
    for restaurant in restaurants:
        print(restaurant)

    order_threads = []

    od1 = threading.Thread(target=order_manager.place_order, kwargs={'user_id': "user1",
                                                                 'orders': {"bendi_macaroni": 3, "samosa_pizza": 2},
                                                                 'restaurant_strategy': SelectionStrategy.LOW_PRICE})

    order_threads.append(od1)

    for thread in order_threads:
        thread.start()

# order_manager.place_order(
#     user_id="user1",
#     orders={"bendi_macaroni": 3, "samosa_pizza": 2},
#     restaurant_strategy=SelectionStrategy.LOW_PRICE,
# )

    od2 = threading.Thread(target=order_manager.place_order, kwargs={'user_id': "user1",
                                                                 'orders': {"bendi_macaroni": 1, "samosa_pizza": 2},
                                                                 'restaurant_strategy': SelectionStrategy.LOW_PRICE})
    order_threads.append(od2)
#
# order_manager.place_order(
#     user_id="user1",
#     orders={"bendi_macaroni": 9, "samosa_pizza": 5},
#     restaurant_strategy=SelectionStrategy.LOW_PRICE,
# )
#

    orders = order_service.get_all_orders()
    for order in orders:
        print(order)

    time.sleep(1)
    restaurants: list[Restaurant] = restaurant_service.get_all_restaurant()
    for restaurant in restaurants:
        print(restaurant, flush=True)


    time.sleep(1)

    restaurants: list[Restaurant] = restaurant_service.get_all_restaurant()
    for restaurant in restaurants:
        print(restaurant, flush=True)
    orders = order_service.get_all_orders()
    for order in orders:
        print(order, flush=True)

    for thread in order_threads:
        if thread.is_alive():
            thread.join()


print("Running Main")
main()