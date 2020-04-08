# -*- coding: utf-8 -*-
#
# Entry point for the add-on into Anki
# Please do not edit this if you do not know what you are doing.
#
# Copyright: (c) 2017 Glutanimate <https://glutanimate.com/>
# License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>

from . import multiple_examples_per_note
from .config import french
if french:
    from .gui import run
    run()
else :
    from .gui import runNonFrench
    runNonFrench()
