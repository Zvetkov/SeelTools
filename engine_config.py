from constants import GLOBAL_PROP_XML, AFFIXES_XML, LOCALIZED_FORMS_QUANTITY, RELATIONSHIP_XML


class EngineConfig(object):
    def __init__(self):
        self.global_properties_path = GLOBAL_PROP_XML
        self.affixes_path = AFFIXES_XML
        self.loc_forms_quantity = LOCALIZED_FORMS_QUANTITY
        self.relationship_path = RELATIONSHIP_XML


theEngineConfig = EngineConfig()
