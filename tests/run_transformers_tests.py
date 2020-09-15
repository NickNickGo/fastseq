# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
""" script for importing transformers tests """

import glob
import sys
import os
import argparse
import logging
import shutil
from git import Repo
from absl.testing import absltest, parameterized
from pip._internal import main as pipmain

FASTSEQ_PATH = os.sep.join(os.path.realpath(__file__).split('/')[0:-2])
TRANSFORMERS_PATH = '/tmp/transformers/'
TRANSFORMERS_GIT_URL = 'https://github.com/huggingface/transformers.git'

class TransformersUnitTests(parameterized.TestCase):
    """Run all the unit tests under transformers"""
    def prepare_env(self):
        """set env variables"""
        #Removing following path since it contains utils directory
        #which clashes with utils.py file in transformers/tests.
        if FASTSEQ_PATH in sys.path:
            sys.path.remove(FASTSEQ_PATH)
        sys.path.insert(0, TRANSFORMERS_PATH)

    def clone_and_build_transformers(self, repo, version):
        """clone and build transformers repo"""
        if os.path.isdir(TRANSFORMERS_PATH):
            shutil.rmtree(TRANSFORMERS_PATH)
        Repo.clone_from(TRANSFORMERS_GIT_URL,
                        TRANSFORMERS_PATH,
                        branch=version)
        pipmain(['install', 'git+https://github.com/huggingface/transformers.git@' +
                    version])
        original_pythonpath = os.environ[
            'PYTHONPATH'] if 'PYTHONPATH' in os.environ else ''
        os.environ[
            'PYTHONPATH'] = TRANSFORMERS_PATH + ':' + original_pythonpath

    @parameterized.named_parameters({
        'testcase_name': 'Normal',
        'without_fastseq_opt': False,
        'transformers_version': 'v3.0.2',
        'blocked_tests': ['test_modeling_reformer.py']
    })
    def test_suites(self, without_fastseq_opt, transformers_version,
                    blocked_tests):
        """run test suites"""
        self.clone_and_build_transformers(TRANSFORMERS_GIT_URL,
                                          transformers_version)
        if not without_fastseq_opt:
            import fastseq  #pylint: disable=import-outside-toplevel
        import pytest #pylint: disable=import-outside-toplevel
        self.prepare_env()
        os.chdir(TRANSFORMERS_PATH)
        blocked_tests_string = (' not '+
                    ' not '.join([test[5:-3] for test in blocked_tests]))
        exit_code = pytest.main(['-sv', '-k'+blocked_tests_string,  './tests/'])
        assert str(exit_code).strip() == 'ExitCode.OK'

if __name__ == "__main__":
    absltest.main()
