import os
import sys
import subprocess
from copy import deepcopy
from config import BASE_INFO
from scripts.utilities import find_addon_names

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

class UpdateError(subprocess.CalledProcessError):
    """Specific class for errors occurring during updates of existing repos.
    """

# ----------------------------------
# flatten_sites
# sites can inherit settings fro other sites
# flatten_sites resolfes this inheritance tree
def flatten_sites(sites):
    """
    sites can inherit settings from other sites
    flatten_sites resolves this inheritance tree
    @SITES            : the global list of sites
    """
    # we allow only one inheritance level
    # check this
    for k, v in list(sites.items()):
        inherits = v.get('inherit')
        vkeys = list(v.keys())
        if inherits:
            # also the inherited site must be deepcopied
            # otherwise we copy the original to our copy that is in fact nothing but a reference fo the original
            inherited = deepcopy(sites.get(inherits))
            if not inherited:
                print('*' * 80)
                print('warning !!! site description %s tries to inherit %s which does not exist' % (
                    k, inherits))
            elif inherited.get('inherit'):
                print('*' * 80)
                print('warning !!! site description %s tries to inherit %s which does also inherit from a site. this is forbidden' % (
                    k, inherits))
                sys.exit()
            # first copy the running site to a temporary var
            # result = v # deepcopy(v)
            # now overwrite what is in the temporary var
            # result.update(inherited)
            # now copy things back but do not overwrite "inherited" values
            # update does not work as this overwrites values that are directories
            for key, val in list(inherited.items()):
                if isinstance(val, dict):
                    # make sure the dic exists otherwise we can not add the items
                    vvkeys = list(v.get(key, {}).keys())
                    if key not in v:
                        v[key] = {}
                    for val_k, val_val in list(val.items()):
                        if isinstance(val_val, list):
                            # v is the element in the inherited site
                            # if v does not have a key we add it with an empty list
                            if val_k not in v[key]:
                                v[key][val_k] = []
                            [v[key][val_k].append(vi)
                                for vi in val_val if vi not in v[key][val_k] and not ('-' + vi in v[key][val_k])]
                            # clean resulting list
                            v[key][val_k] = [vi for vi in v[key]
                                                [val_k] if not vi.startswith('-')]
                        elif isinstance(val_val, dict):
                            # v is the site into which we inherit (the parent)
                            # key is the key in the child
                            # val is the value in the child
                            # val_val
                            if val_k not in v[key]:
                                # so we have a target dict
                                v[key][val_k] = {}
                            # now add elements to the the target dict
                            target = v[key][val_k]
                            for val_val_k, val_val_v in list(val_val.items()):
                                # we do an other level of hierarchy
                                if isinstance(val_val_v, list):
                                    if val_val_k not in target:
                                        target[val_val_k] = []
                                    sub_target = target[val_val_k]
                                    for tk in val_val_v:
                                        # should it be possible to decuct keys???
                                        if tk not in sub_target:
                                            sub_target.append(tk)
                                elif isinstance(val_val_v, dict):
                                    if val_val_k not in target:
                                        target[val_val_k] = {}
                                    sub_target = target[val_val_k]
                                    for val_val_v_k, val_val_v_v in list(val_val_v.items()):
                                        sub_target[val_val_v_k] = val_val_v_v
                                else:
                                    if val_val_k not in target:
                                        target[val_val_k] = val_val_v
                        else:
                            if val_k not in vvkeys:
                                v[key][val_k] = val_val
                elif isinstance(val, list):
                    existing = v.get(key, [])
                    v[key] = existing + \
                        [vn for vn in val if vn not in existing]
                else:
                    # ['site_name', 'servername', 'db_name']:
                    if key in vkeys:
                        continue

# --------------------------------------------
# _construct_sa
# return list of urls to download addons from
# --------------------------------------------
def _construct_sa(site_name, site_addons, skip_list):
    """
    """
    added = []
    name = ''
    for a in (site_addons or []):
        names = find_addon_names(a)
        for name in names:
            if not name:
                continue
            if name and name in skip_list:
                continue
            ap = a.get('add_path')
            if ap:
                p = os.path.normpath(
                    '%s/%s/addons/%s' % (BASE_INFO['erp_server_data_path'], site_name, ap))
            else:
                p = os.path.normpath(
                    '%s/%s/addons' % (BASE_INFO['erp_server_data_path'], site_name))
            if p not in added:
                added.append(p)
    return '\n'.join(['    local %s' % a for a in added])

