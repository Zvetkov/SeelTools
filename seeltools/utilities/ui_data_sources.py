from utilities.value_classes import AnnotatedValue, DisplayType
from gameobjects.prototype_info import thePrototypeInfoClassDict

DisplayTypeDataSource = \
    {DisplayType.CLASS_NAME: thePrototypeInfoClassDict.keys(),
     DisplayType.RESOURCE_ID: "",
     DisplayType.SKIN_NUM: ""}
