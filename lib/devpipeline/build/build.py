#!/usr/bin/python3

import os.path
import os

import devpipeline.build.cmake
import devpipeline.toolsupport


# Every builder supported should have an entry in this dictionary.  The key
# needs to match whatever value the "build" key is set to in build.conf, and
# the value should be a function that takes a component and returns a Builder.
_builder_lookup = {
    "cmake": devpipeline.build.cmake.make_cmake,
    "nothing": lambda c, cw: cw(devpipeline.build.CommonBuilder())
}


def _make_builder(component, common_wrapper):
    """
    Create and return a Builder for a component.

    Arguments
    component - The component the builder should be created for.
    """
    return devpipeline.toolsupport.tool_builder(component, "build",
                                                _builder_lookup,
                                                common_wrapper)


class SimpleBuild(devpipeline.toolsupport.SimpleTool):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def configure(self, src_dir, build_dir):
        self._call_helper("Configuring", self.real.configure,
                          src_dir, build_dir)

    def build(self, build_dir):
        self._call_helper("Building", self.real.build,
                          build_dir)

    def install(self, build_dir, path=None):
        self._call_helper("Installing", self.real.install,
                          build_dir, path)


def build_task(target, *args, **kwargs):
    """
    Build a target.

    Arguments
    target - The target to build.
    """

    build_path = target.get("dp.build_dir")
    if not os.path.exists(build_path):
        os.makedirs(build_path)
    builder = _make_builder(
        target, lambda r: SimpleBuild(real=r, *args, **kwargs))
    builder.configure(target.get("dp.src_dir"), build_path)
    builder.build(build_path)
    if "no_install" not in target:
        builder.install(build_path, path=target.get("install_path",
                                                    "install"))
