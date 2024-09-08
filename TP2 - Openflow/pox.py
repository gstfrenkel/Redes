#!/bin/sh -

# Copyright 2011-2012 James McCauley
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# If you have PyPy in a directory called pypy alongside pox.py, we
# use it.
# Otherwise, we try to use a Python interpreter called python3, which
# is a good idea if it's there.
# We fall back to just "python" and hope that works.

from pox.boot import boot

if __name__ == '__main__':
    boot()
