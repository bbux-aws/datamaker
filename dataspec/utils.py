"""
Module for storing package wide common functions
"""
import os
import importlib
import logging
import dataspec.casters as casters


def load_custom_code(code_path):
    """
    Loads user custom code
    :param code_path: path to the custom code to load
    :return: None
    """
    if not os.path.exists(code_path):
        raise Exception(f'Path to {code_path} not found.')
    try:
        spec = importlib.util.spec_from_file_location("python_code", str(code_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as exception:
        logging.warning("Couldn't load custom Python code: %s: %s", code_path, str(exception))


def is_affirmative(key, config, default=False):
    """
    Checks if the config value is one of true, yes, or on (case doesn't matter), default is False
    :param key: to check
    :param config: to lookup key in
    :param default: if not found, False if not specified
    :return: if the config is present and is one of true, yes, or on
    """
    value = str(config.get(key, default)).lower()
    return value in ['yes', 'true', 'on']


def load_config(field_spec, loader):
    """
    Loads the config and any secondary configs into one object
    :param field_spec: that should contain config
    :param loader: system spec loader
    :return: the full config
    """
    if not isinstance(field_spec, dict):
        return {}

    config = field_spec.get('config', {})
    refkey = config.get('configref')
    if refkey:
        configref = loader.get_ref_spec(refkey)
        config.update(configref.get('config', {}))
    return config


def get_caster(config):
    """ returns the caster object from the config """
    return casters.get(config.get('cast'))


def any_key_exists(config, keys):
    """ checks if any of the keys exist in the config object """
    return any(key in config for key in keys)


def update_config(spec, key, value):
    """ add the key and value to the spec config """
    config = spec.get('config', {})
    config[key] = value
    spec['config'] = config
    return spec
