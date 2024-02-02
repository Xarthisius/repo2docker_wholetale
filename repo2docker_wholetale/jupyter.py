# -*- coding: utf-8 -*-

"""Main module."""

import os

from .wholetale import WholeTaleBuildPack


class JupyterWTStackBuildPack(WholeTaleBuildPack):
    def detect(self, buildpack="PythonBuildPack"):
        return super().detect(buildpack=buildpack)

    def get_build_script_files(self):
        """Dict of files to be copied to the container image for use in building"""
        files = {}
        for k, v in {
            "base/healthcheck.py": "/healthcheck.py",
            "base/jupyter_notebook_config.py": "${HOME}/.jupyter/jupyter_notebook_config.py",
        }.items():
            files[os.path.join(os.path.dirname(__file__), k)] = v

        files.update(super().get_build_script_files())
        return files
