# -*- coding: utf-8 -*-

"""Main module."""

import datetime
import json
import os

from repo2docker.buildpacks.r import RBuildPack
from repo2docker.buildpacks.python import PythonBuildPack


class WholeTaleBuildPack(PythonBuildPack):

    major_pythons = {"2": "2.7", "3": "3.10"}
    _wt_env = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def binder_path(self, path):
        """
        Locate a build file in a default dir.

        .wholetale takes precedence over default binder behaviour
        """
        for possible_config_dir in (".wholetale", "binder"):
            if os.path.exists(possible_config_dir):
                return os.path.join(possible_config_dir, path)
        return path

    def get_build_script_files(self):
        """
        Generate a mapping for files injected into the container.

        Dict of files to be copied to the container image for use in building.
        This is copied before the `build_scripts` & `assemble_scripts` are
        run, so can be executed from either of them.
        It's a dictionary where the key is the source file path in the host
        system, and the value is the destination file path inside the
        container image.
        """
        files = super().get_build_script_files()
        files.update(
            {
                os.path.join(
                    os.path.dirname(__file__), "base/healthcheck.py"
                ): "/healthcheck.py"
            }
        )
        return files

    def detect(self, buildpack=None):
        if not os.path.exists(self.binder_path("environment.json")):
            return False

        with open(self.binder_path("environment.json"), "r") as fp:
            env = json.load(fp)

        try:
            return env["config"]["buildpack"] == buildpack
        except (KeyError, TypeError):
            return False

    @property
    def wt_env(self):
        if self._wt_env is None:
            with open(self.binder_path("environment.json"), "r") as fp:
                env = json.load(fp)
            self._wt_env = dict([_.split("=") for _ in env["config"]["environment"]])
        return self._wt_env


class WholeTaleRBuildPack(RBuildPack):

    major_pythons = {"2": "2.7", "3": "3.10"}

    def binder_path(self, path):
        """
        Locate a build file in a default dir.

        .wholetale takes precedence over default binder behaviour
        """
        for possible_config_dir in (".wholetale", "binder"):
            if os.path.exists(possible_config_dir):
                return os.path.join(possible_config_dir, path)
        return path

    @property
    def python_version(self):
        """If environment.yaml is present, use PythonBuildPack's parent (conda) python_version"""
        if self.environment_yaml:
            return super(PythonBuildPack, self).python_version
        else:
            return super(RBuildPack, self).python_version

    def set_checkpoint_date(self):
        if not self.checkpoint_date:
            # no R snapshot date set through runtime.txt so set
            # to a reasonable default -- the last month of the previous
            # quarter
            self._checkpoint_date = self.mran_date(datetime.date.today())
            self._runtime = "r-{}".format(str(self._checkpoint_date))

    def detect(self, buildpack=None):
        if not os.path.exists(self.binder_path("environment.json")):
            return False

        with open(self.binder_path("environment.json"), "r") as fp:
            env = json.load(fp)

        try:
            if env["config"]["buildpack"] == buildpack:
                self.set_checkpoint_date()
                return True
        except (KeyError, TypeError):
            return False
