from collections import namedtuple

Column = namedtuple("Column", ["fieldName", "type", "digit", "nullable", "foreignKey"])