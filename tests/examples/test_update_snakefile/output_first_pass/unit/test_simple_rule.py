#!/usr/bin/env python3
testdir = "tests/examples/test_update_snakefile/output"  # noqa
rulename = "simple_rule"  # noqa
import os  # noqa
import shutil  # noqa
import subprocess as sp  # noqa
import sys  # noqa
from pathlib import Path, PurePosixPath  # noqa
from tempfile import TemporaryDirectory  # noqa

sys.path.insert(0, os.path.dirname(__file__))  # noqa

import common  # noqa


def test_function():

    with TemporaryDirectory() as tmpdir:
        rundir = Path(tmpdir) / "rundir"  # FOR TESTING: PurePosixPath(testdir + "/out_" + rulename)
        workspace_path = PurePosixPath("{}/unit/{}/workspace".format(testdir, rulename))
        expected_path = PurePosixPath("{}/unit/{}/expected".format(testdir, rulename))

        # Copy data to the temporary workdir.
        shutil.copytree(workspace_path, rundir)

        # Run the test job.
        sp.check_output(
            [
                "python",
                "-m",
                "snakemake",
                "all",
                "-f",
                "-j1",
                "--keep-target-files",
                "--use-conda",
                "--conda-frontend",
                "mamba",
                "--snakefile",
                "{}/workflow/Snakefile".format(rundir),
                "--directory",
                rundir,
            ]
        )

        # Check the output byte by byte using cmp.
        # To modify this behavior, you can inherit from common.OutputChecker in here
        # and overwrite the method `compare_files(generated_file, expected_file),
        # also see common.py.

        common.OutputChecker(workspace_path, expected_path, rundir).check()
