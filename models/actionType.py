from .aColumnsDef import Column

tableName = 'action_type'
columns = [
    Column("name", "String", 20, False, ""),
    Column("color", "String", 10, False, ""),
    Column("is_default_type", "Integer", 0, False, ""),
]