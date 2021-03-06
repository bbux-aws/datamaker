"""
Module for handling nested types
"""
from typing import Dict, Any
import dataspec


class NestedSupplier(dataspec.ValueSupplierInterface):
    """
    Implementation for Nested Value Supplier
    """

    def __init__(self,
                 field_supplier_map: Dict[str, dataspec.ValueSupplierInterface],
                 count_supplier: dataspec.ValueSupplierInterface,
                 as_array: bool):
        self.field_supplier_map = field_supplier_map
        self.count_supplier = count_supplier
        self.as_array = as_array

    def next(self, iteration: int):
        count = int(self.count_supplier.next(iteration))
        if count == 0:
            if self.as_array:
                return []
            return None
        if count > 1:
            vals = [self._single_pass(iteration + i) for i in range(count)]
            return vals
        # this is dict
        vals = self._single_pass(iteration)
        if self.as_array:
            return [vals]
        return vals

    def _single_pass(self, iteration: int) -> Dict[str, Any]:
        return {key: supplier.next(iteration) for key, supplier in self.field_supplier_map.items()}


@dataspec.registry.types('nested')
def configure_nested_supplier(spec, loader):
    """ configure the supplier for nested types """
    fields = spec['fields']
    keys = [key for key in fields.keys() if key not in loader.RESERVED]
    config = dataspec.utils.load_config(spec, loader)
    count_supplier = dataspec.suppliers.count_supplier_from_data(config.get('count', 1))
    as_array = dataspec.utils.is_affirmative('as_array', config)

    field_supplier_map = {}
    # each non reserved key should have a valid spec as a value
    for key in keys:
        nested_spec = fields[key]
        if nested_spec.get('type') == 'nested':
            supplier = configure_nested_supplier(nested_spec, loader)
        else:
            supplier = loader.get_from_spec(nested_spec)
        field_supplier_map[key] = supplier
    return NestedSupplier(field_supplier_map, count_supplier, as_array)
