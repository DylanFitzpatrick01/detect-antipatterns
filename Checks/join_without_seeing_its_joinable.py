import clang.cindex
from typing import List
from alerts import Alert

"""
TODO Write Description
"""

class Check():
    def analyse_cursor(self, cursor: clang.cindex.Cursor) -> List[Alert]:
        alert_list = list()

        for node in  cursor.translation_unit.cursor.walk_preorder():
            if node.kind == clang.cindex.CursorKind.CALL_EXPR and node.spelling == "join":
                                alert_list.append(Alert(cursor.translation_unit, cursor.extent,+
                                        "Recomend Add a joinable check "
                                        "\n if (t.joinable())"
                                        "\n t.join"))