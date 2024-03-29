#!/usr/bin/env python

"""
Common code for unit testing of rules generated with Snakemake 6.0.0.
"""

import gzip
import os
import subprocess as sp
from pathlib import Path

import pytest

exclude_ext = [".tbi", ".html"]
# TODO: Read in a list of extensions to exclude from the config.  See issue #16.


class OutputChecker:
    def __init__(self, data_path, expected_path, workdir):
        self.data_path = data_path
        self.expected_path = expected_path
        self.workdir = workdir

    def check(self):
        input_files = set(
            (Path(path) / f).relative_to(self.data_path)
            for path, subdirs, files in os.walk(self.data_path)
            for f in files
        )
        expected_files = set(
            (Path(path) / f).relative_to(self.expected_path)
            for path, subdirs, files in os.walk(self.expected_path)
            for f in files
        )
        unexpected_files = set()
        for path, subdirs, files in os.walk(self.workdir):
            for f in files:
                f = (Path(path) / f).relative_to(self.workdir)
                if str(f).startswith(".snakemake"):
                    continue
                if "/log/" in str(f):
                    continue
                if "/logs/" in str(f):
                    continue
                if "/performance_benchmarks/" in str(f):
                    continue
                if str(f).endswith(tuple(exclude_ext)):
                    continue
                if f in expected_files:
                    self.compare_files(self.workdir / f, self.expected_path / f)
                elif f in input_files:
                    # ignore input files
                    pass
                else:
                    unexpected_files.add(f)
        if unexpected_files:
            raise ValueError(
                "Unexpected files:\n{}".format("\n".join(sorted(map(str, unexpected_files))))
            )

    def compare_files(self, generated_file, expected_file):
        if str(generated_file).lower().endswith((".vcf.gz", ".vcf")):
            gen = process_file(generated_file)
            exp = process_file(expected_file)
            assert gen == exp
        else:
            sp.check_output(["cmp", generated_file, expected_file])


def process_file(infile):
    if str(infile).lower().endswith(".gz"):
        with gzip.open(infile, mode="rt") as f:
            n = remove_headers(f)
    else:
        with open(infile, "r") as f:
            n = remove_headers(f)
    return n


def remove_headers(f):
    n = []
    for line in (line for line in f if not line.startswith("##")):
        n.append(line)
    return n
