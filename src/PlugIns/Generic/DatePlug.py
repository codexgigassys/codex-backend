# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import datetime

from PlugIns.PlugIn import PlugIn


class DatePlug(PlugIn):

    def __init__(self, sample=None):
        PlugIn.__init__(self, sample)

    def getName(self):
        return "date"

    def getVersion(self):
        return 1

    def process(self):
        new_date = datetime.datetime.now()
        old_date = self.sample.getLastValue("date")
        if old_date == None:
            return new_date

        if new_date < old_date:
            return new_date

        return old_date
