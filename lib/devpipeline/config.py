#!/usr/bin/python3

import configparser
import os.path
import os

import devpipeline.version


class ConfigFinder:
    def __init__(self, filename):
        self.filename = filename

    def read_config(self):
        config = configparser.ConfigParser(
            interpolation=configparser.ExtendedInterpolation())
        config.read(self.filename)

        return config


_overrides_root = "{}/{}".format(os.path.expanduser("~"),
                                 ".dev-pipeline.d/overrides.d")
_profile_file = "{}/{}".format(os.path.expanduser("~"),
                               ".dev-pipeline.d/profiles.conf")
_version_id = (devpipeline.version.major << 24) | (
               devpipeline.version.minor << 16) | (
               devpipeline.version.patch << 8)


def find_config():
    previous = ""
    current = os.getcwd()
    while previous != current:
        check_path = "{}/build.cache".format(current)
        if os.path.isfile(check_path):
            return ConfigFinder(check_path)
        else:
            previous = current
            current = os.path.dirname(current)
    raise Exception("Can't find build cache")


def _override_deleted(config, package):
    raw_overrides = config.get("dp.override_list", fallback="")
    if raw_overrides:
        override_list = [x.strip() for x in raw_overrides]
    else:
        override_list = []
    for override in override_list:
        override_path = "{}/{}/{}.conf".format(
            _overrides_root, override, package)
        if not os.path.isfile(override_path):
            print("missing {}".format(override_path))
            return True
    return False


def _updated_override(config_data, cache_time):
    override_list = [x.strip() for x in config_data.get(
        "DEFAULT", "dp.overrides", fallback="").split(",")]
    for package in config_data.sections():
        for override in override_list:
            override_path = "{}/{}/{}.conf".format(
                _overrides_root, override, package)
            if os.path.isfile(override_path) and (
                    os.path.getmtime(override_path) > cache_time):
                return True
            if _override_deleted(config_data[package], package):
                return True
    return False


def _updated_software(config):
    config_version = config.get("DEFAULT", "dp.version", fallback="0")
    return _version_id > int(config_version, 16)


def _cache_outdated(config_data, build_cache_path):
    cache_time = os.path.getmtime(build_cache_path)
    input_files = [
        config_data.get("DEFAULT", "dp.build_config"),
        _profile_file
    ]
    for input_file in input_files:
        mt = os.path.getmtime(input_file)
        if cache_time < mt:
            return True
    if _updated_software(config_data):
        return True
    else:
        return _updated_override(config_data, cache_time)


def rebuild_cache(config, force=False):
    data = config.read_config()
    if force or _cache_outdated(data, config.filename):
        return write_cache(ConfigFinder(data.get("DEFAULT",
                                                 "dp.build_config")),
                           ProfileConfig(data.get("DEFAULT",
                                                  "dp.profile_name")),
                           data.get("DEFAULT", "dp.overrides"),
                           data.get("DEFAULT", "dp.build_root"))
    else:
        return data


class ValueAppender():
    def __init__(self):
        self.profile_vals = {}

    def add(self, key, value):
        if key not in self.profile_vals:
            self.profile_vals[key] = value
        else:
            self.profile_vals[key] += " {}".format(value)


class ProfileConfig:
    def __init__(self, profile_names=None, handler=ValueAppender()):
        self.names = profile_names
        self.handler = handler

    def _add_profile_values(self, profile_config, names):
        def add_each_key(items):
            for key, value in items:
                self.handler.add(key, value)

        for name in names:
            if profile_config.has_section(name):
                add_each_key(profile_config.items(name))
            else:
                raise Exception(
                    "Profile {} doesn't exist".format(name))

    def _get_specific_profile(self, profile_config):
        if self.names:
            names = [x.strip() for x in self.names.split(",")]
            # Build profile_vals with everything from all the profiles.
            self._add_profile_values(profile_config, names)
            return self.handler.profile_vals
        else:
            return profile_config.defaults()

    def read_config(self):
        if os.path.isfile(_profile_file):
            return self._get_specific_profile(
                ConfigFinder(_profile_file).read_config())


def _add_root_values(config, state_variables):
    defaults = config.defaults()
    defaults["dp.build_root"] = state_variables["build_dir"]
    defaults["dp.src_root"] = state_variables["src_dir"]


def _make_src_path(config, state):
    section = state["section"]
    src_path = config.get(section, "src_path", raw=True, fallback=None)
    if not src_path:
        return "${{dp.src_root}}/{}".format(section)
    else:
        return src_path


_ex_values = {
    "dp.build_dir":
        lambda config, state:
            "${{dp.build_root}}/{}".format(state["section"]),
    "dp.src_dir": _make_src_path
}


def _add_section_values(config, state_variables):
    for section in config.sections():
        state_variables["section"] = section
        for key, fn in _ex_values.items():
            config[section][key] = fn(config, state_variables)


def _add_default_values(config, state_variables):
    for key, value in state_variables.items():
        config[key] = value


def _add_profile_values(config, profile_config):
    for key, value in profile_config.items():
        if key not in config:
            config[key] = value


def _validate_config_dir(build_dir, cache_name):
    files = os.listdir(build_dir)
    if files:
        if not cache_name in files:
            raise Exception(
                "{} doesn't look like a build directory".format(build_dir))


def _find_overrides(target, overrides):
    override_list = ""
    values = []
    for current_override in overrides:
        override_file = "{}/{}/{}.conf".format(_overrides_root,
                                               current_override, target)
        if os.path.isfile(override_file):
            if override_list:
                override_list += ",{}".format(current_override)
            else:
                override_list = current_override
            values.append(ConfigFinder(override_file).read_config())
    return {
        "overrides": override_list,
        "values": values
    }


def _override_append(config, overrides):
    for key, value in overrides.items():
        if key in config:
            config[key] += " {}".format(value)
        else:
            config[key] = value


def _override_set(config, overrides):
    for key, value in overrides.items():
        config[key] = value


def _override_delete(config, overrides):
    for key, value in overrides.items():
        del config[key]


_override_rules = {
    "append": _override_append,
    "set": _override_set,
    "delete": _override_delete
}


def _apply_override(config, target, overrides, override_names):
    for override in overrides:
        for section in override.sections():
            fn = _override_rules.get(section)
            if fn:
                fn(config[target], override[section])
            else:
                raise Exception("Unknown override section: {}".format(section))
    config[target]["dp.applied_overrides"] = override_names


def _apply_overrides(config, overrides):
    override_list = [x.strip() for x in overrides.split(",")]
    for target in config.sections():
        override = _find_overrides(target, override_list)
        values = override.get("values")
        if values:
            _apply_override(config, target, values, override["overrides"])


def write_cache(config_reader, profile_config_reader, overrides,
                build_dir, cache_name="build.cache"):
    config = config_reader.read_config()
    profile_section = profile_config_reader.read_config()
    if not os.path.isdir(build_dir):
        os.makedirs(build_dir)
    else:
        _validate_config_dir(build_dir, cache_name)

    config_abs = os.path.abspath(config_reader.filename)
    state_variables = {
        "src_dir": os.path.dirname(config_abs)
    }
    if os.path.isabs(build_dir):
        state_variables["build_dir"] = build_dir
    else:
        state_variables["build_dir"] = "{}/{}".format(os.getcwd(), build_dir)

    _add_section_values(config, state_variables)
    _add_profile_values(config.defaults(), profile_section)
    _add_default_values(config.defaults(), {
        "dp.build_config": config_abs,
        "dp.build_root": state_variables["build_dir"],
        "dp.overrides": overrides,
        "dp.profile_name": profile_config_reader.names,
        "dp.src_root": state_variables["src_dir"],
        "dp.version": format(_version_id, '02x')
    })
    _apply_overrides(config, overrides)
    with open("{}/{}".format(build_dir, cache_name), 'w') as output_file:
        config.write(output_file)
    return config
