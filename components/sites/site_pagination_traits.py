#!/usr/bin/python
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "utils", "parameters"))
from pagination import *

class SitePaginationTraits(PaginationTraitsBase):

    def __init__(self, a_page_size, a_start):
        PaginationTraitsBase.__init__(self, a_page_size=a_page_size, a_page_start=a_start, a_fetch_size_key_field="fetch_size", a_start_key_field="first_key", a_next_key_field="next_key", a_data_page_key_field="items")
