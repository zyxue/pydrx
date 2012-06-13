import os

import yaml

from obj import System

os.environ['YAML'] = "pydr.yml"

yamlf = os.getenv("YAML")
if not yamlf:
    raise ValueError("yaml file not found, serious problem!")
params = yaml.load(open(yamlf))

sysname = params['sysname']
rootdir = params['rootdir']
misc_params = params['MISC']
sys = System(sysname, rootdir, misc_params)
