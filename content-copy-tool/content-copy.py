#!/usr/bin/env python

# Passthrough for backwards compatibility
from __future__ import print_function
print("This command for the CCT is deprecated. Please try the `content-copy` command instead.")
import contentcopytool.content_copy as cct
cct.main()