def add_etree_attribute_if_propery_exist(etreeObject, attributeName, propertyName, prototype):
    if hasattr(prototype, propertyName) and not property_equel_default(prototype, propertyName):
        etreeObject.set(attributeName, str(getattr(prototype, propertyName)))


def property_equel_default(prototype, propertyName):
    defaultPrototype = prototype.__class__(prototype.theServer)
    v1 = getattr(prototype, propertyName)
    v2 = getattr(defaultPrototype, propertyName)
    if v1 == v2:
        return True
    else:
        return (v1 == '' or v1 is None) == (v2 == '' or v2 is None)
