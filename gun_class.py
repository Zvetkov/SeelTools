from base_classes import VehiclePart
from logger import logger


class Gun(VehiclePart):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        VehiclePart.__init__(self, name, prototype, belong,
                             position, rotation, skin, logo)
        logger.warning(f"Not implemented class {self.__name__}")
        pass


class BulletLauncher(Gun):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        Gun.__init__(self, name, prototype, belong,
                     position, rotation, skin, logo)
        logger.warning(f"Not implemented class {self.__name__}")
        pass


class LocationPusher(Gun):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        Gun.__init__(self, name, prototype, belong,
                     position, rotation, skin, logo)
        logger.warning(f"Not implemented class {self.__name__}")
        pass


class MinePusher(Gun):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        Gun.__init__(self, name, prototype, belong,
                     position, rotation, skin, logo)
        logger.warning(f"Not implemented class {self.__name__}")
        pass


class Mortar(Gun):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        Gun.__init__(self, name, prototype, belong,
                     position, rotation, skin, logo)
        logger.warning(f"Not implemented class {self.__name__}")
        pass


class MortarVolleyLauncher(Mortar):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        Mortar.__init__(self, name, prototype, belong,
                        position, rotation, skin, logo)
        logger.warning(f"Not implemented class {self.__name__}")
        pass


class PlasmaBunchLauncher(Gun):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        Gun.__init__(self, name, prototype, belong,
                     position, rotation, skin, logo)
        logger.warning(f"Not implemented class {self.__name__}")
        pass


class RocketLauncher(Gun):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        Gun.__init__(self, name, prototype, belong,
                     position, rotation, skin, logo)
        logger.warning(f"Not implemented class {self.__name__}")
        pass


class RocketVolleyLauncher(RocketLauncher):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        RocketLauncher.__init__(self, name, prototype, belong,
                                position, rotation, skin, logo)
        logger.warning(f"Not implemented class {self.__name__}")
        pass


class ThunderboltLauncher(Gun):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        Gun.__init__(self, name, prototype, belong,
                     position, rotation, skin, logo)
        logger.warning(f"Not implemented class {self.__name__}")
        pass


class TurboAcceleratorPusher(Gun):
    def __init__(self, name: str, prototype: str, belong: int,
                 position: str, rotation: str, skin: int, logo: int):
        Gun.__init__(self, name, prototype, belong,
                     position, rotation, skin, logo)
        logger.warning(f"Not implemented class {self.__name__}")
        pass
