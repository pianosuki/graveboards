from sqlalchemy.sql.selectable import CTE


class HashableCTE:
    def __init__(self, cte: CTE):
        self.cte = cte

    def __hash__(self):
        return hash(self.cte.name)

    def __eq__(self, other):
        if not isinstance(other, HashableCTE):
            return False

        return self.cte.name == other.cte.name
