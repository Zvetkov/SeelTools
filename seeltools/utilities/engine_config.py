from utilities.constants import (GLOBAL_PROP_XML, LOCALIZED_FORMS_QUANTITY,
                                 UI_EDIT_STRINGS_XML, AFFIXES_STRINGS_XML)


class EngineConfig:
    def __init__(self):
        self.global_properties = GLOBAL_PROP_XML
        self.loc_forms_quantity = LOCALIZED_FORMS_QUANTITY
        self.ui_edit_strings = UI_EDIT_STRINGS_XML
        self.affixes_strings = AFFIXES_STRINGS_XML


theEngineConfig = EngineConfig()
