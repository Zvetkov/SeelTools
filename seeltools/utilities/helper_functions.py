def value_equel_default(value, default_value):
    if value == default_value:
        return True
    else:
        return (value == '' or value is None) and (default_value == '' or default_value is None)