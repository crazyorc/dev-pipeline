#!/usr/bin/python3

import os.path
import unittest

import loader

import devpipeline.config.override
import devpipeline.config.paths

_config_dir = "{}/../files".format(os.path.dirname(os.path.abspath(__file__)))


class TestConfigOverride(unittest.TestCase):
    def _validate(self, expected, override, actual):
        self.assertTrue(override in expected)
        expected_overrides = expected[override]
        self.assertEqual(len(expected_overrides), len(actual))
        for key, value in expected_overrides.items():
            self.assertTrue(key in actual)
            self.assertEqual(value, actual[key])

    def test_empty(self):
        def _dont_call(override, values):
            raise Exception("Shouldn't have been called")

        count = devpipeline.config.override.read_all_overrides(
            devpipeline.config.paths.get_overrides_root(_config_dir),
            ["empty"], "foo", _dont_call)
        self.assertEqual(0, count)

    def test_append(self):
        expected = {
            "simple": {
                "val.append": "abc",
                "lav.append": "xyz"
            }
        }
        count = devpipeline.config.override.read_all_overrides(
            devpipeline.config.paths.get_overrides_root(_config_dir),
            ["simple"], "foo",
            lambda override, vals:
                self._validate(expected, override, vals))
        self.assertEqual(1, count)

    def test_multiappend(self):
        expected = {
            "simple": {
                "val.append": "abc",
                "lav.append": "xyz"
            },
            "trivial": {
                "val.append": "ijk"
            }
        }
        count = devpipeline.config.override.read_all_overrides(
            devpipeline.config.paths.get_overrides_root(_config_dir),
            ["simple", "trivial"], "foo",
            lambda override, vals:
                self._validate(expected, override, vals))
        self.assertEqual(2, count)


if __name__ == "__main__":
    unittest.main()
