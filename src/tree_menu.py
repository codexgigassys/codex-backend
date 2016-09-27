# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.

from TreeMenu import *

package=__import__("TreeMenu")
tree=[]
ids={}
for module_name in package.__all__:
    module=getattr(package, module_name)
    tree.append(module.tree_element)
    ids.update(module.id_element)