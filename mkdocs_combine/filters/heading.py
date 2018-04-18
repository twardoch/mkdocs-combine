# Copyright 2018 Luke Frisken <l.frisken@gmail.com>
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
#

import re

class HeadingFilter(object):
    """Strips out a heading from the document"""

    def __init__(self, heading):
        self.heading = heading

    def run(self, lines):
        """Filter method"""
        
        ret = []

        removing_heading = False
        removing_level = 0

        for line in lines:

            m = re.search(r'^(#+)(.*)', line)

            if m is not None:
                # found a heading which matches
                
                heading_level = m.group(1)
                heading_name = m.group(2).strip()

                if (heading_name == self.heading):
                    if removing_heading:
                        if removing_level <= heading_level:
                            removing_heading = True
                            removing_level = heading_level

                    else:
                        removing_heading = True
                        removing_level = heading_level
                else:
                    if removing_level <= removing_level:
                        removing_heading = False

            skip_line = False
            
            if (not removing_heading) or skip_line:
                ret.append(line)
            else:
                print("removing line:", line)

        return ret
