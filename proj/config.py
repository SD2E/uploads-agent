#!/usr/bin/env python

# Configuration loader from YML files with
# optional ENV-based overrides

# Usage: from config import settings
import os
import yaml

settings = {}

HERE = os.path.dirname(os.path.abspath(__file__))
PWD = os.getcwd()
ROOT = '/'
'''
Implements some configuration conventions:

1. A Reactor can be configured via a config.yml
file in its top-level directory. The configuration
file can have arbitrary content so long as it can
be resolved from YML to JSON.
2. Any first- or second-level key with a string
value can be overridden at run-time by an env
named _REACTOR_LEVEL1_LEVEL2
3. The configuration is exported as a dict in
the 'settings' variable
'''


def read_config():
    """Reads config.yml into 'settings' with optional ENV overrides"""
    config = settings.copy()
    # File-based configuration.
    places = [ROOT, PWD, HERE]
    for p in places:
        fname = os.path.join(p, "config.yml")
        if os.path.isfile(fname):
            try:
                with open(fname, "r") as conf:
                    read_config = yaml.load(conf, Loader=yaml.FullLoader)
                    config = config.copy()
                    config.update(read_config)
                break
            except Exception:
                pass

    # TODO - Check for duplicate keys coming in from ENV
    # TODO - Check that get/set from ENV is successful
    for level1 in config.keys():
        if type(config[level1]) is str:
            env_var = '_REACTOR_' + level1
            env_var = env_var.upper()
            if os.environ.get(env_var):
                config[level1] = os.environ.get(env_var)
        elif type(config[level1]) is dict:
            for level2 in config[level1].keys():
                if type(config[level1][level2]) is str:
                    env_var = '_REACTOR_' + level1 + '_' + level2
                    env_var = env_var.upper()
                    if os.environ.get(env_var):
                        config[level1][level2] = os.environ.get(env_var)
        else:
            pass

    return config


settings = read_config()
