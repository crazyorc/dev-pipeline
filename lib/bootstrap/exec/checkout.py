#!/usr/bin/python3
"""This modules does the checkout of code from SCM."""

import bootstrap.scm.scm
import bootstrap.common


def main(args=None):
    # pylint: disable=missing-docstring
    checkout = bootstrap.common.TargetTool([
        bootstrap.scm.scm.scm_task
    ], prog="dev-pipeline checkout", description="Checkout repositories")
    bootstrap.common.execute_tool(checkout, args)


if __name__ == '__main__':
    main()
