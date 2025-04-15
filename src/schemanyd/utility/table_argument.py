# This module contains classes for representing table-level metadata (constraints and indexes)
# in the Schemanyd Graph. These are table-associated definitions that are tied to the table
# itself (as opposed to graph-level relationships).

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .graph import Table, Column

# - - - LEVEL 1 - TableArgument - - -

class TableArgument:

    def __init__(self, table: "Table", name: str):
        """
        - Base container for table-level metadata used by the Schemanyd Graph.
        - Holds a reference to the Schemanyd Table object and a human-friendly name.
        - Represents any table-associated definition that is tied to the table itself (as opposed to graph-level relationships).

        Subclasses share a common SQL keyword prefix that indicates their type.

        | Table Constraints -   | Column Constraints -   | Index   |
        |-----------------------|------------------------|---------|
        | `CONSTRAINT`          | `COLUMN`               | `INDEX` |
        | UNIQUE                | NOT NULL               | INDEX   |
        | PRIMARY KEY           | DEFAULT                |         |
        | FOREIGN KEY           |                        |         |
        | CHECK                 |                        |         |        
        """
        self.table = table
        self.name = name

# - - - LEVEL 2 - Constraint & Index - - -

class Constraint(TableArgument):

    def __init__(self, table: "Table", constraint_type: str, name: str):
        """ Parent class for all constraints. """
        super().__init__(table, name)
        self.constraint_type = constraint_type


class Index(TableArgument):

    def __init__(self, table: "Table", columns: List["Column"], name: str):
        """
        Indexes are not used for Schemanyds logic, they are included for completeness.

        They are similar yet conceptually separate from CONSTRAINTs and use the SQL `INDEX` keyword.

        Parameters
        ----------
        table: Table
            The table the index belongs to.
        columns: List[Column]
            The list of columns included in the index.
        name: str
            The name of the index.
        """
        super().__init__(table, name)
        self.columns = columns

# - - - LEVEL 3 - TableConstraint & ColumnConstraint - - -

class TableConstraint(Constraint):

    def __init__(self, table: "Table", constraint_type: str, columns: List["Column"], name: str):
        """
        These constraints are set using the SQL keyword `CONSTRAINT`:
        `UNIQUE`, `PRIMARY KEY`, `FOREIGN KEY`, `CHECK`

        Parameters
        ----------
        table: Table
            The table the constraint belongs to.
        constraint_type: str
            The type of the constraint (`UNIQUE`, `PRIMARY KEY`, `FOREIGN KEY` or `CHECK`).
        columns: List[Column]
            The columns the constraint applies to.
        name: str
            The name of the constraint.
        """
        super().__init__(table, constraint_type, name)
        self.columns = columns


class ColumnConstraint(Constraint):

    def __init__(self, table: "Table", constraint_type: str, column: "Column"):
        """
        These constraints are set using the SQL keyword `COLUMN`:
        `NOT NULL` and `DEFAULT`

        Column constraints are directly applied to columns and do not have separate names.
        They are identified by their constraint_type and the column they apply to.

        There is no attribute to store the `DEFAULT` value. Currently the priority is on
        representing the structure. This would anyway be handled by the database.

        Similar for `NOT NULL`, if the constraint exists, it means the column cannot be null.

        Parameters
        ----------
        table: Table
            The table the constraint belongs to.
        constraint_type: str
            The type of the constraint (either NOT NULL or DEFAULT).
        column: Column
            The column the constraint is applied to, can't be a list.
        """
        # Column constraints don't have names, so we generate one from column name and type
        name = f"{constraint_type.lower().replace(' ', '_')}_{column.name}"
        super().__init__(table, constraint_type, name)
        self.column = column

# - - - LEVEL 4.1 - TableConstraints - - -

class UniqueConstraint(TableConstraint):

    def __init__(self, table: "Table", columns: List["Column"], name: str):
        """
        Ensures unique values across one or more columns.

        Parameters
        ----------
        table: Table
            The table the constraint belongs to.
        columns: List[Column]
            The columns that must have unique values (composite unique if multiple).
        name: str
            The name of the constraint.
        """
        super().__init__(table, "UNIQUE", columns, name)


class PrimaryKeyConstraint(TableConstraint):

    def __init__(self, table: "Table", columns: List["Column"], name: str):
        """
        Uniquely identifies each row in a table.

        Parameters
        ----------
        table: Table
            The table the constraint belongs to.
        columns: List[Column]
            The columns that form the primary key (composite if multiple).
        name: str
            The name of the constraint.
        """
        super().__init__(table, "PRIMARY KEY", columns, name)


class ForeignKeyConstraint(TableConstraint):

    def __init__(self, table: "Table", columns: List["Column"], referenced_table: "Table", referenced_columns: List["Column"], name: str):
        """
        Links columns to columns in another table, establishing relationships.

        Parameters
        ----------
        table: Table
            The table the constraint belongs to.
        columns: List[Column]
            The local columns that reference another table.
        referenced_table: Table
            The table being referenced.
        referenced_columns: List[Column]
            The columns in the referenced table.
        name: str
            The name of the constraint.
        """
        super().__init__(table, "FOREIGN KEY", columns, name)
        self.referenced_table = referenced_table
        self.referenced_columns = referenced_columns


class CheckConstraint(TableConstraint):

    def __init__(self, table: "Table", columns: List["Column"], condition: str, name: str):
        """
        Enforces a boolean condition on column values.

        Parameters
        ----------
        table: Table
            The table the constraint belongs to.
        columns: List[Column]
            The columns involved in the check condition.
        condition: str
            The SQL boolean expression that must be true.
        name: str
            The name of the constraint.
        """
        super().__init__(table, "CHECK", columns, name)
        self.condition = condition

# - - - LEVEL 4.2 - ColumnConstraints - - -

class NotNullConstraint(ColumnConstraint):

    def __init__(self, table: "Table", column: "Column"):
        """
        Ensures a column cannot contain NULL values.

        Column constraints do not have explicit names - they are identified by the column they apply to.

        Parameters
        ----------
        table: Table
            The table the constraint belongs to.
        column: Column
            The column that cannot be null.
        """
        super().__init__(table, "NOT NULL", column)


class DefaultConstraint(ColumnConstraint):

    def __init__(self, table: "Table", column: "Column", default_value: str):
        """
        Provides a default value when no value is specified during insertion.

        Column constraints do not have explicit names - they are identified by the column they apply to.

        Parameters
        ----------
        table: Table
            The table the constraint belongs to.
        column: Column
            The column that receives the default value.
        default_value: str
            The default value expression (e.g., "CURRENT_TIMESTAMP", "'active'", "0").
        """
        super().__init__(table, "DEFAULT", column)
        self.default_value = default_value
