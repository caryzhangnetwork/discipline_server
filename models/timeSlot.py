from .aColumnsDef import Column

tableName = 'time_slot'
columns = [
    Column("create_date", "String", 60, False, ""),
    Column("score_id", "Integer", 0, False, "score_board"),
    Column("create_by", "Integer", 0, False, "user"),
]