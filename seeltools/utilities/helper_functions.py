from seeltools.utilities.value_classes import AnnotatedValue, SavingType


def vector_short_to_string(value):
    return f'{value["x"]} {value["y"]}'


def vector_to_string(value):
    return f'{value["x"]} {value["y"]} {value["z"]}'


def vector_long_to_string(value):
    return f'{value["x"]} {value["y"]} {value["z"]} {value["w"]}'


def should_be_saved(annotatedValue: AnnotatedValue):
    if (
        annotatedValue.saving_type == SavingType.REQUIRED
        or annotatedValue.saving_type == SavingType.REQUIRED_SPECIFIC
        or (
            annotatedValue.value != annotatedValue.default_value
            and (annotatedValue.value != '' or annotatedValue.value is not None)
        )
    ):
        return True
    else:
        return False


def add_value_to_node(node, annotatedValue: AnnotatedValue, func=lambda x: str(x.value)):
    if should_be_saved(annotatedValue):
        node.set(annotatedValue.name, func(annotatedValue))


def add_value_to_node_as_child(node, annotatedValue: AnnotatedValue, func):
    if should_be_saved(annotatedValue):
        result = func(annotatedValue)
        if isinstance(result, list):
            node.extend(result)
        else:
            node.append(result)
