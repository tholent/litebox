#!/usr/bin/env python3
# Copyright 2026 Chris Wells
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Check that every source file in the repository carries the Apache-2.0 license header.

Usage: python3 tests/check-headers.py
Looks at the files git tracks (plus new ones not yet ignored) ending in .html, .js, .mjs or .py.
Prints each file missing the header, then one line: "litebox-headers: ok=N missing=M". Exit 0 only when M=0.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = (".html", ".js", ".mjs", ".py")
NEEDLE = "Licensed under the Apache License, Version 2.0"


def main():
    listed = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT,
                            capture_output=True, text=True, check=True).stdout.split("\n")
    files = sorted(f for f in listed if f.endswith(SOURCE) and (ROOT / f).is_file())
    missing = [f for f in files if NEEDLE not in "".join((ROOT / f).read_text(encoding="utf-8").splitlines(True)[:40])]
    for f in missing:
        print("missing license header:", f)
    print("litebox-headers: ok=%d missing=%d" % (len(files) - len(missing), len(missing)))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
