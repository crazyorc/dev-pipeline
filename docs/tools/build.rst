build
=====

Synopsis
--------
.. code::

    dev-pipeline build [-h] [--executor EXECUTOR] [targets [targets ...]]


Description
-----------
This tool builds one or more targets along with their dependencies.  The
specific order of dependencies isn't guaranteed, but any package will be built
before packages that depend on it.

If no targets are specified, all targets will be built.


Options
-------
  -h, --help           show this help message and exit
  --executor EXECUTOR  The amount of verbosity to use. Options are "quiet"
                       (print no extra information), "verbose" (print
                       additional information), "dry-run" (print commands to
                       execute, but don't run them), and "silent" (print
                       nothing). Regardless of this option, errors are always
                       printed. (default: quiet)



Config Options
--------------
* :code:`build` - (**Required**) The build tool to use.  It must be an option
  listed in Builders_.
* :code:`install_path` - The path *within the build directory* to install a
  package.  If unspecified, :code:`install` will be used.
* :code:`no_install` - Prevent a package from being installed.


Builders
--------
* cmake_ - Build using CMake.
* nothing - No build step.  This is useful for dependencies that don't produce
  any artifacts, but are needed for some reason.


.. _cmake: ../builder/cmake.rst
