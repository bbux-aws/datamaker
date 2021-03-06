"""
Module for handling geo types
"""
import json

from dataspec import registry, suppliers, ValueSupplierInterface, SpecException
import dataspec.schemas as schemas
from dataspec.utils import load_config, is_affirmative

GEO_LAT_KEY = 'geo.lat'
GEO_LONG_KEY = 'geo.long'
GEO_PAIR_KEY = 'geo.pair'


class GeoSupplier(ValueSupplierInterface):
    """
    Default implementation for generating geo related values
    """

    def __init__(self, wrapped):
        self.wrapped = wrapped

    def next(self, iteration):
        value = self.wrapped.next(iteration)
        return value


@registry.schemas(GEO_LAT_KEY)
def get_geo_lat_schema():
    return schemas.load(GEO_LAT_KEY)


@registry.schemas(GEO_LONG_KEY)
def get_geo_long_schema():
    return schemas.load(GEO_LONG_KEY)


@registry.schemas(GEO_PAIR_KEY)
def get_geo_pair_schema():
    return schemas.load(GEO_PAIR_KEY)


@registry.types(GEO_LAT_KEY)
def configure_geo_lat(field_spec, loader):
    """ configures value supplier for geo.lat type """
    return _configure_lat_type(field_spec, loader)


@registry.types(GEO_LONG_KEY)
def configure_geo_long(field_spec, loader):
    """ configures value supplier for geo.long type """
    return _configure_long_type(field_spec, loader)


@registry.types(GEO_PAIR_KEY)
def configure_geo_pair(field_spec, loader):
    """ configures value supplier for geo.pair type """
    config = load_config(field_spec, loader)
    long_supplier = _configure_long_type(field_spec, loader)
    lat_supplier = _configure_lat_type(field_spec, loader)
    join_with = config.get('join_with', ',')
    as_list = is_affirmative('as_list', config, False)
    lat_first = is_affirmative('lat_first', config)
    combine_config = {
        'join_with': join_with,
        'as_list': as_list
    }
    if lat_first:
        return suppliers.combine([lat_supplier, long_supplier], combine_config)
    return suppliers.combine([long_supplier, lat_supplier], combine_config)


def _configure_long_type(spec, loader):
    return _configure_geo_type(spec, loader, -180.0, 180.0, '_long')


def _configure_lat_type(spec, loader):
    return _configure_geo_type(spec, loader, -90.0, 90.0, '_lat')


def _configure_geo_type(spec, loader, default_start, default_end, suffix):
    config = load_config(spec, loader)
    precision = config.get('precision', 4)
    if not str(precision).isnumeric():
        raise SpecException(f'precision for geo should be valid integer: {json.dumps(spec)}')
    start, end = _get_start_end(config, default_start, default_end, suffix)
    return GeoSupplier(suppliers.random_range(start, end, precision))


def _get_start_end(config, default_start, default_end, suffix):
    if 'bbox' in config:
        bbox = config['bbox']
        if not isinstance(bbox, list) or len(bbox) != 4:
            raise SpecException('Bounding box must be list of size 4 with format: [min Longitude, min Latitude, max Longitude, max Latitude]')
        if 'lat' in suffix:
            default_start = bbox[1]
            default_end = bbox[3]
        else:
            default_start = bbox[0]
            default_end = bbox[2]
    # start_lat or start_long overrides bbox or defaults
    start = config.get('start' + suffix, default_start)
    # end_lat or end_long overrides bbox or defaults
    end = config.get('end' + suffix, default_end)
    return start, end
