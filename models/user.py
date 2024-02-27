from .aColumnsDef import Column

tableName = 'user'
columns = [
    Column("name", "String", 20, False, ""),
    Column("password", "String", 20, False, ""),
    Column("total_score", "Integer", 0, False, ""),
    Column("profile_pic", "String", 255, False, "")
]