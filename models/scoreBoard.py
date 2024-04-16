from .aColumnsDef import Column

tableName = 'score_board'
columns = [
    Column("action_type", "Integer", 0, False, "action_type"),
    Column("reward_type", "Integer", 0, False, ""),
    Column("time", "String", 20, True, ""),
    Column("duration", "String", 20, True, ""),
    Column("score", "Integer", 0, False, ""),
]