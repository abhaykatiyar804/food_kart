from pytest import fixture

from tdd_food_kart_1.core.restaurant import MenuItem, Restaurant


@fixture(name="restaurant")
def initialise_restaurant():
    menu = {"idli": 10, "dosa": 20}
    restaurant = Restaurant(name="R1", menu=menu, capacity=15)
    return restaurant


class TestRestaurant:

    def test_initialisation(self, restaurant): ...

    def test_update_menu(self, restaurant):
        updated_menu = {"idli": 50, "rajma": 50}
        restaurant = restaurant.update_menu(updated_menu)
        for item, price in updated_menu.items():
            menu = restaurant.menu[item]
            assert menu.price == price
