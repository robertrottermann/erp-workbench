import yaml
from io import StringIO
from pprint import pformat
from scripts.bcolors import bcolors
import os

"""this module provides functionality to read and write yaml files
"""

def read_yaml_file(path, vals={}):
    """read a yaml file and replace all variables used in it

    Arguments:
        path {string} -- path to the yaml file
    """
    with open(path) as f:
        raw_yaml_data = f.read()
    # it can be hard to find an error when varibales are not well define
    # so check the content line by line
    counter = -1
    raw_yaml_data_stripped = []
    for line in raw_yaml_data.split('\n'):
        counter += 1
        if line.strip().startswith('#'):
            continue
        try:
            line % vals
            raw_yaml_data_stripped.append(line)
        except Exception:
            print(bcolors.FAIL)
            print('*' * 80)
            print('file %s' % path)
            print('line %s: %s has a problem' % (counter, line))
            print(bcolors.ENDC)
            raise
    raw_yaml_data = '\n'.join(raw_yaml_data_stripped) % vals
    try:
        return yaml.load(StringIO(raw_yaml_data))
    except yaml.parser.ParserError as e:
        print(bcolors.FAIL)
        print('*' * 80)
        print('file %s can not be parsed' % path)
        print(bcolors.ENDC)
        raise



def check_and_update_base_defaults(yaml_files, vals, results={}):
    """read a list of yaml files and construct python files that can be imported
    We have three elements involved in this process:
    1. config/config_data/xx_info.py
       this file has the actual data. If it is newer than the rest, it is taken
    2. if config/config_data/xx_info.py does not exist or is not newer than
       config/xx.yaml, it is generated from this file.
       config/xx.yaml was copied from config/xx.yaml.in if it did not exist (in config/__init__.py)
    3. When config/config_data/xx_info.py is generated, default values are read from
       templates/xx.yaml.
       This is to make sure, that all the values needed exist, as the user could somehow have 
       deleted it when editing the config/xx.yaml file.

    Arguments:
        yaml_files {list of tuples} -- tuples with (
            path to the yaml file, 
            path to the datafile to be constructed,
            {path to yaml with defaults}
        )
        vals {dictionary} : values that are used in the yaml files

    Keyword Arguments:
        results {dict} -- dictionary with the data loaded (default: {{}})

    Returns:
        boolean -- flag telling whether the data had to be constructed
    """

    must_restart = False
    for yaml_data in yaml_files:
        if len(yaml_data) == 3:
            # we have to construct a yaml file with its variable replaced
            yaml_file_path, data_file_path, yaml_file_path_defaults = yaml_data
        elif len(yaml_data) == 2:
            yaml_file_path_defaults = ''
            yaml_file_path, data_file_path = yaml_data
        else:
            print(bcolors.FAIL)
            print('*' * 80)
            print('badly formated entry for check_and_update_base_defaults') 
            print(yaml_data)
            print(bcolors.ENDC)
            raise ValueError
        if os.path.exists(yaml_file_path):
            # compare file dates
            # check if folder exists:
            if not os.path.exists(os.path.dirname(data_file_path)):
                os.makedirs(os.path.dirname(data_file_path))
            if os.path.exists(data_file_path) and  \
                os.path.getmtime(data_file_path) >= os.path.getmtime(yaml_file_path):
                # we have to flag, that we did not load this module
                results[yaml_file_path] = {}
                continue
            # read defaults 
            yaml_data = {}
            if yaml_file_path_defaults and os.path.exists(yaml_file_path_defaults):
                yaml_data = read_yaml_file(yaml_file_path_defaults, vals)
            # red the real thing, update defaults
            yaml_data.update(read_yaml_file(yaml_file_path, vals))
            new_line = '%s = %s\n'
            new_yaml_data = ""
            for k,v in yaml_data.items():
                new_yaml_data += new_line % (k, pformat(v))
            with open(data_file_path, 'w') as f:
                f.write(new_yaml_data)

            must_restart = True
            results[yaml_file_path] = yaml_data
        else:
            print(bcolors.WARNING)
            print('*' * 80)
            print('%s does not exist', yaml_file_path)
            print(bcolors.ENDC)
            continue

    return must_restart
    