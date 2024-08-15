import abc
import threading
import time
import uuid
from abc import ABC
from collections import defaultdict, namedtuple
from enum import IntEnum, Enum
from typing import Union, Optional
from queue import Queue


class IOrderManagerObserver(ABC):

    @abc.abstractmethod
    def complete_order(self, restaurant_id: str, order_id: str): ...


class ISubject(ABC):

    @abc.abstractmethod
    def subscribe_observer(self, observer: IOrderManagerObserver): ...


class RestaurantNotFound(Exception): ...


class SelectionStrategy(Enum):
    LOW_PRICE = "low_price"


RestaurantCost = namedtuple("SelectedRestaurant", ["restaurant", "cost"])

Orderid_Order = namedtuple("Orderid_Order", ["order_id", "order"])


class MenuItem:
    def __init__(self, item: str, price: int):
        self.price: int = price
        self.item: str = item

    @classmethod
    def update_item(cls, item: str, price: int) -> "MenuItem":
        return cls(item=item, price=price)

    def __eq__(self, other: Union[str, "MenuItem"]):
        if isinstance(other, str):
            return self.item == other
        return self.item == other.item

    def __hash__(self):
        return hash(self.item)

    def __repr__(self):
        return f"{self.item}: {self.price}"


class Restaurant(ISubject):
    def __init__(self, name: str, menu: dict, capacity: int):
        self.restaurant_name: str = name
        self.restaurant_id: str = uuid.uuid4().hex
        self.capacity: int = capacity
        self.menu: dict[str, MenuItem] = {
            item: MenuItem(item, price) for item, price in menu.items()
        }
        self.capacity_consume: int = 0
        self.orders: Queue[Orderid_Order] = Queue()
        self.observers: Optional[IOrderManagerObserver] = None
        self.__lock = threading.Lock()

    def __repr__(self):

        return f"{self.restaurant_name} , menu: {list(self.menu.values())}, capacity: {self.capacity}, capacity_in_use:{self.capacity_consume}"

    def subscribe_observer(self, observer: IOrderManagerObserver):
        self.observers = observer

    def update_menu(self, menu: dict):
        for item, price in menu.items():
            self.menu[item] = MenuItem(item, price)
        return self

    def is_item_available(self, item):
        return item in self.menu

    def calculate_cost(self, item, quantity):
        return self.menu[item].price * quantity

    def can_prepare_order(self, orders: "OrderEvent") -> bool:
        with self.__lock:
            order = orders.order_details.orders
            order_id = orders.order_details.order_id
            can_process = (
                    all(item in self.menu for item, quantity in order.items())
                    and self.capacity_consume + sum(order.values()) <= self.capacity
            )
            if can_process:
                self.orders.put(Orderid_Order(order_id, order))
                self.capacity_consume += sum(order.values())
            return can_process

    def process_order(self) -> str:
        with self.__lock:
            order: Orderid_Order = self.orders.get()
            for item, quantity in order.order.items():
                time.sleep(1)
                print(f"Processing {item} of {quantity} quantity", flush=True)
            self.capacity_consume -= sum(order.order.values())
            self.observers.complete_order(self.restaurant_id, order_id=order.order_id)


class IRestaurantRepo(ABC):

    @abc.abstractmethod
    def add_restaurant(self, restaurant: Restaurant) -> None: ...

    @abc.abstractmethod
    def get_restaurant(self, restaurant_name: str) -> Optional[Restaurant]: ...

    @abc.abstractmethod
    def get_all_restaurant(self) -> list[Restaurant]: ...


class IOrderRepo(ABC):

    @abc.abstractmethod
    def add_order(self, order: "Order"): ...

    @abc.abstractmethod
    def get_order_by_id(
            self, restaurant_id: str, order_id: str
    ) -> Optional["Order"]: ...

    @abc.abstractmethod
    def get_all_orders(self) -> list["Order"]: ...


class OrderStore(IOrderRepo):

    def __init__(self):
        self.__storage = {"orders": defaultdict(dict)}

    def add_order(self, order: "Order"):
        self.__storage["orders"][order.restaurant_id][order.order_id] = order

    def get_order_by_id(self, restaurant_id: str, order_id: str) -> Optional["Order"]:
        return self.__storage["orders"].get(restaurant_id).get(order_id)

    def get_all_orders(self) -> list["Order"]:
        orders = list(self.__storage["orders"].values())
        return [value for order in orders for key, value in order.items()]


class RestaurantStore(IRestaurantRepo):

    def __init__(self):
        self.__storage = {"restaurants": defaultdict(Restaurant)}

    def add_restaurant(self, restaurant: Restaurant) -> None:
        self.__storage["restaurants"][restaurant.restaurant_name] = restaurant

    def get_restaurant(self, restaurant_name: str) -> Optional[Restaurant]:
        return self.__storage["restaurants"].get(restaurant_name)

    def get_all_restaurant(self) -> list[Restaurant]:
        return list(self.__storage["restaurants"].values())


class RestaurantService:

    def __init__(self, restaurant_store: IRestaurantRepo):
        self.restaurant_store = restaurant_store

    def register_restaurant(
            self, name: str, menu: dict, capacity: int, order_manager: IOrderManagerObserver
    ):
        restaurant = Restaurant(name, menu, capacity)
        restaurant.subscribe_observer(observer=order_manager)
        self.restaurant_store.add_restaurant(restaurant)

    def update_restaurant_menu(self, restaurant_name: str, menu: dict):
        restaurant = self.restaurant_store.get_restaurant(
            restaurant_name=restaurant_name
        )
        restaurant = restaurant.update_menu(menu)
        self.restaurant_store.add_restaurant(restaurant)

    def get_restaurant(self, restaurant_name: str):
        restaurant = self.restaurant_store.get_restaurant(restaurant_name)
        if restaurant is None:
            raise RestaurantNotFound()
        return restaurant

    def get_all_restaurant(self) -> list[Restaurant]:
        return self.restaurant_store.get_all_restaurant()


class OrderService:

    def __init__(self, order_store: IOrderRepo):
        self.order_store = order_store

    def add_order(self, order):
        self.order_store.add_order(order)

    def get_order_service(self, restaurant_id: str, order_id: str) -> "Order":
        return self.order_store.get_order_by_id(restaurant_id, order_id)

    def get_all_orders(self) -> list["Order"]:
        return self.order_store.get_all_orders()


class OrderState(IntEnum):
    ORDER_INITIATE = 0
    SELECTED_RESTAURANT = 1
    ORDER_PLACE = 2
    ORDER_PROCESSING = 3
    # ORDER_COMPLETE = 4


class OrderStatus(Enum):
    PLACED = "placed"
    COMPLETED = "completed"


class OrderDetail:
    def __init__(self, orders: dict, user_id: str):
        self.user_id: str = user_id
        self.orders: dict = orders
        self.selected_restaurants: list[RestaurantCost] = []
        self.order_id: str = uuid.uuid4().hex
        self.qualifying_restaurant: Optional[Restaurant] = None
        self.cost: int = 0

    def set_restaurants(self, restaurants: list[RestaurantCost]) -> None:
        self.selected_restaurants = restaurants

    def set_qualifying_restaurant(self, restaurant: Restaurant):
        self.qualifying_restaurant = restaurant

    def set_cost(self, cost: int):
        self.cost = cost


class OrderEvent:

    def __init__(self, order_state: OrderState, order_details: OrderDetail):
        self.order_state: OrderState = order_state
        self.order_details: OrderDetail = order_details

    def set_order_state(self, state: OrderState):
        self.order_state = state
        return self


class Order:
    def __init__(
            self,
            cost,
            restaurant_name=None,
            restaurant_id=None,
            order_detail=None,
            user_id=None,
            order_id=None,
    ):
        self.cost: int = cost
        self.order_status: OrderStatus = OrderStatus.PLACED
        self.restaurant_name: Optional[str] = restaurant_name
        self.restaurant_id: Optional[str] = restaurant_id
        self.order_detail: Optional[dict] = order_detail
        self.user_id: Optional[str] = user_id
        self.order_id: Optional[str] = order_id

    def __repr__(self):
        return f"order_id: {self.order_id}, status: {self.order_status.value}, restaurant_name: {self.restaurant_name}, user_id: {self.user_id}, cost:{self.cost}"

    def complete_order(self):
        self.order_status = OrderStatus.COMPLETED

    @classmethod
    def generate_order(cls, order_event: OrderEvent):
        payload = {
            "cost": order_event.order_details.cost,
            "restaurant_name": order_event.order_details.qualifying_restaurant.restaurant_name,
            "restaurant_id": order_event.order_details.qualifying_restaurant.restaurant_id,
            "order_detail": order_event.order_details.orders,
            "user_id": order_event.order_details.user_id,
            "order_id": order_event.order_details.order_id,
        }
        return cls(**payload)


class RestaurantSelectionStrategy(ABC):

    @abc.abstractmethod
    def get_restaurant(self, order: dict) -> list[Restaurant]: ...


class LowestPriceRestaurantStrategy(RestaurantSelectionStrategy):

    def __init__(self, restaurant_service: RestaurantService):
        self.restaurant_service = restaurant_service

    def get_restaurant(self, order: dict) -> list[RestaurantCost]:
        restaurants: list[Restaurant] = self.restaurant_service.get_all_restaurant()
        available_restaurant = []
        order_details = order.copy()
        can_be_place = []
        for restaurant in restaurants:
            if all(restaurant.is_item_available(item) for item in order_details):
                available_restaurant.append(restaurant)

        return self.calculate_cost(available_restaurant, order_details)

    def calculate_cost(
            self, restaurants: list[Restaurant], order_details: dict
    ) -> list[RestaurantCost]:

        selected = []
        min_cost = float("inf")
        for restaurant in restaurants:
            total_cost = sum(
                restaurant.calculate_cost(item, quantity)
                for item, quantity in order_details.items()
            )
            if total_cost < min_cost:
                min_cost = total_cost
                restaurant_cost = RestaurantCost(restaurant, min_cost)
                selected = [restaurant_cost]
            elif total_cost == min_cost:

                restaurant_cost = RestaurantCost(restaurant, min_cost)
                selected.append(restaurant_cost)

        return selected


class OrderManager(IOrderManagerObserver):

    def __init__(
            self, restaurant_service: RestaurantService, order_service: OrderService
    ):
        self.restaurant_service = restaurant_service
        self.order_service = order_service
        self.restaurant_selection_strategy: SelectionStrategy = None

        self.state_machine = {
            OrderState.SELECTED_RESTAURANT: self.restaurant_selection_handler,
            OrderState.ORDER_PLACE: self.place_order_handler,
            OrderState.ORDER_PROCESSING: self.order_processing_handler,
            # OrderState.ORDER_COMPLETE: self.order_complete_handler,
        }

        # self.current_state = OrderState.ORDER_PLACE

    def set_strategy(self, strategy: SelectionStrategy):
        self.restaurant_selection_strategy = strategy

    def place_order(
            self, user_id: str, orders: dict, restaurant_strategy: SelectionStrategy
    ):
        self.set_strategy(restaurant_strategy)
        handler = self.state_machine[OrderState.SELECTED_RESTAURANT]
        # self.current_state = OrderState.SELECTED_RESTAURANT
        order_details = OrderDetail(user_id=user_id, orders=orders)
        event = OrderEvent(
            order_state=OrderState.SELECTED_RESTAURANT, order_details=order_details
        )
        # threading.Thread(target=handler, args=(event,)).start()
        handler(event)

    def restaurant_selection_handler(self, order_event: OrderEvent):

        orders = order_event.order_details.orders
        restaurant = None
        if self.restaurant_selection_strategy == SelectionStrategy.LOW_PRICE:
            _strategy = LowestPriceRestaurantStrategy(self.restaurant_service)
            restaurants: list[RestaurantCost] = _strategy.get_restaurant(orders)
        else:
            restaurants = None

        try:
            if restaurants:
                order_event.order_details.set_restaurants(restaurants)
                event = order_event.set_order_state(OrderState.ORDER_PLACE)
                handler = self.state_machine[OrderState.ORDER_PLACE]
                handler(event)
            else:
                raise RestaurantNotFound()
        except RestaurantNotFound:
            print(f"Can not place order , no restaurant found!!", flush=True)

    def place_order_handler(self, order_event: OrderEvent):
        selected_restaurants: list[RestaurantCost] = (
            order_event.order_details.selected_restaurants
        )
        qualifying_restaurant = []
        for restaurant_cost in selected_restaurants:
            if restaurant_cost.restaurant.can_prepare_order(orders=order_event):
                qualifying_restaurant.append(restaurant_cost)

        # if we have multiple restaurant , there cost will be same
        if qualifying_restaurant:
            order_event.order_details.set_qualifying_restaurant(
                qualifying_restaurant[0].restaurant
            )
            order_event.order_details.set_cost(qualifying_restaurant[0].cost)
            order: Order = Order.generate_order(order_event=order_event)
            self.order_service.add_order(order)
            print(
                f"{order_event.order_details.qualifying_restaurant.restaurant_name}, {order.order_id} "
            )
            event = order_event.set_order_state(OrderState.ORDER_PROCESSING)
            handler = self.state_machine[OrderState.ORDER_PROCESSING]
            handler(event)
        else:
            print('Restaurnat Not Available', flush=True)

    def order_processing_handler(self, order_event: OrderEvent):
        restaurant = order_event.order_details.qualifying_restaurant
        restaurant.process_order()
        #
        # event = order_event.set_order_state(OrderState.ORDER_COMPLETE)
        # handler = self.state_machine[OrderState.ORDER_COMPLETE]
        # handler(event)
        # orderservice will listen to order and mark the order complete

    # def order_complete_handler(self, order_event: OrderEvent):
    #     pass
    #
    def complete_order(self, restaurant_id, order_id):
        order: Order = self.order_service.get_order_service(
            restaurant_id=restaurant_id, order_id=order_id
        )
        order.complete_order()
        self.order_service.add_order(order)
        print(f"order complete ::: {order}")


