# coding: utf-8
'''
File: report.py
Author: Oliver Zscheyge
Description:
    Report superclass.
'''

from .localizable import Localizable

class Report(Localizable):
    """Superclass for all Reports.
    """
    def __init__(self, ID="", language="", brief="", description=""):
        super(Report, self).__init__(ID, language, brief, description)

    def execute(self, docs, args):
        buf = list()
        return "\n".join(buf)

