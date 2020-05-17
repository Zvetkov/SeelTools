from enum import Enum
from copy import deepcopy


class DisplayType(Enum):
    CLASS_NAME = 0  # as list edit with suggestions from all class names
    RESOURCE_ID = 1  # display as ResourceName from dropdown with available resource types
    PROTOTYPE_NAME = 2  # as list edit with suggestions from all prototype names
    SKIN_NUM = 3  # skin list dropdown available for model, idealy with texture preview
    MODIFICATION_INFO = 4  # list of objects, add/remove functions, TBD UI solution
    VEHICLE_DESCRIPTION = 5  # list of vehicle descriptions, similar to 4
    AFFIX_LIST = 6


class GroupType(Enum):
    INTERNAL = 0  # prototype ids and other internal info that is not useful for direct editing, ex prototype id
    GENERAL = 1
    PRIMARY = 2
    SECONDARY = 3
    VISUAL = 4  # textures, models, icons


class SavingType(Enum):
    COMMON = 0  # saving behaviour implemented in PrototypeInfo
    SPECIFIC = 1  # saving behaviour implemented in Class by itself
    RESOURCE = 2  # saving behaviout for ResourceType specifically
    IGNORE = 3  # ignore property during saving. Default if GroupType is INTERNAL


class AnnotatedValue(object):
    def __init__(self,
                 value,  # any Type,
                 name: str,  # service name to map with display name and description
                 group_type: int = None,
                 saving_type: int = None,
                 default_value=None,  # same as value
                 initial_value=None,  # same as value
                 display_type: int = None,  # types with fancy display widget(for ex: enums to choose dropdown)
                 read_only: bool = False,
                 is_dirty: bool = False):
        self.value = value
        self.name = name
        self.group_type = group_type

        if group_type == GroupType.INTERNAL and saving_type is None:
            self.saving_type = SavingType.IGNORE
        elif saving_type is None:
            self.saving_type = SavingType.COMMON
        else:
            self.saving_type = saving_type

        # we want to create new AnnotatedValues only in Init of classes and after that manipulate them directly
        # in that case default_value always should be same as value
        if default_value is None:
            self.default_value = deepcopy(value)
        else:
            self.default_value = default_value

        self.initial_value = deepcopy(value)
        self.display_type = display_type
        self.read_only = read_only
        self.is_dirty = is_dirty
