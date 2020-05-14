def add_etree_attribute_if_propery_exist(etreeObject, attributeName, propertyName, prototype):
    if hasattr(prototype, propertyName):
        etreeObject.set(attributeName, str(getattr(prototype, propertyName)))
