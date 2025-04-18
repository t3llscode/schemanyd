# This class is creating a generic representation of the schema,
# allowing for better encapsulation and manipulation of the graph structure.

# Preinstalled Imports
from email.policy import default
from typing import Dict, List, Tuple, Type

# SQLAlchemy Imports
from sqlalchemy import ForeignKeyConstraint as SQLA_ForeignKeyConstraint
from sqlalchemy import PrimaryKeyConstraint as SQLA_PrimaryKeyConstraint
from sqlalchemy import UniqueConstraint as SQLA_UniqueConstraint
from sqlalchemy import CheckConstraint as SQLA_CheckConstraint

# Schemanyd Imports
from .table_argument import TableArgument, Index, TableConstraint, ColumnConstraint, UniqueConstraint, PrimaryKeyConstraint, ForeignKeyConstraint, CheckConstraint, NotNullConstraint, DefaultConstraint


def register_converters():
    """ Once the classes are defined, this function registers the available schema converters. """
    Graph.register_converter("sqlalchemy", SQLAlchemySchemaConverter)

#  - - - - - - - - - - GRAPH - - - - - - - - - -

class Graph:

    _SCHEMA_CONVERTERS: Dict[str, Type["SchemaConverter"]] = {}


    def __init__(self, schema, schema_type: str = "sqlalchemy"):
        """
        Create a traceable Graph representation of a database schema. Currently supports only SQLAlchemy schemas.

        Parameters:
            schema: The MetaData object to convert into a Schemanyd Graph.
            schema_type: The schema type to use. Currently only "sqlalchemy" is supported and is the default.
        """

        self.schema = schema
        self.schema_type = schema_type

        converter = self._load_converter(schema_type)
        self.nodes, self.edges = converter.convert(schema)


    def __repr__(self):
        return f"Graph(nodes={self.nodes})"


    @classmethod
    def register_converter(cls, schema_type: str, converter_cls: Type["SchemaConverter"]) -> None:
        """ Register a converter of type SchemaConverter for a specific schema type. """
        cls._SCHEMA_CONVERTERS[schema_type] = converter_cls


    @classmethod
    def get_supported_schema_types(cls) -> List[str]:
        """ Returns a sorted list of supported schema types. """
        return sorted(cls._SCHEMA_CONVERTERS.keys())


    def _load_converter(self, schema_type: str) -> "SchemaConverter":
        """ Try to load (return) the SchemaConverter object for the given schema type. """
        try:
            converter_cls = self._SCHEMA_CONVERTERS[schema_type]
        except KeyError as exc:
            available = ", ".join(self.get_supported_schema_types()) or "none"
            raise ValueError(
                f"Error: Unsupported schema type '{schema_type}', available types are: [{available}]"
            ) from exc
        return converter_cls()

#  - - - - - GRAPH ELEMENTS - - - - -
# - - - Table - - -

class Table:  # Node

    def __init__(self, name: str):
        """
        Table objects contain information about the table's columns, constraints and relationships.
        
        The tables of the database are represented as nodes in the graph.
        """
        self.name = name
        self.columns: Dict[str, "Column"] = {}
        self.relationships: List["Relationship"] = []
        self.arguments: List[TableArgument] = []


    def add_column(self, column: "Column") -> None:
        self.columns[column.name] = column


    def get_column_by_name(self, name: str, throw_error: bool = False) -> "Column":
        column = self.columns.get(name, None)
        if throw_error and column is None:
            raise ValueError(f"Column '{name}' not found in table '{self.name}'")
        return column


    def add_relationship(self, relationship: "Relationship") -> None:
        if relationship not in self.relationships:
            self.relationships.append(relationship)


    def add_argument(self, argument: TableArgument) -> None:
        if argument not in self.arguments:  # this check might be unnecessary
            self.arguments.append(argument)


    def __repr__(self):
        return f"Table({self.name}, {list(self.columns.values())}, {self.relationships})"

# - - - Column - - -

class Column:

    def __init__(self, table: Table, name: str, data_type: str, nullable: bool = True, default: str = None, is_primary_key: bool = False, is_foreign_key: bool = False):
        """
        Column objects contain information about the column and the constraints associated with it.

        Within the Graph they are not directly represented as nodes or edges, but their properties contribute to the overall structure and are linked to tables and relationships.
        """
        self.table = table
        self.name = name
        self.data_type = data_type
        self.nullable = nullable
        self.default = default  # not necessary for schemanyd
        self.is_primary_key = is_primary_key
        self.is_foreign_key = is_foreign_key
        self.arguments: List[TableArgument] = []  # not sure if necessary for schemanyd


    def add_argument(self, argument: TableArgument) -> None:
        if argument not in self.arguments:
            self.arguments.append(argument)


    def __repr__(self):
        modifiers = []
        if self.is_primary_key:
            modifiers.append("PK")
        if self.is_foreign_key:
            modifiers.append("FK")
        if not self.nullable:
            modifiers.append("NOT NULL")
        modifier_str = f" [{' '.join(modifiers)}]" if modifiers else ""
        return f"{self.name} ({self.data_type}){modifier_str}"

# - - - Relationship - - -

class Relationship:  # Edge

    def __init__(self, source: Column, target: Column):
        """
        Relationship objects represent the connections between columns in different tables.

        Within the Graph they are represented as edges connecting the nodes / tables of source and target.
        """
        self.source = source
        self.target = target
        self.relationship_type = self._determine_relationship_type()


    def __repr__(self):
        return f"Relationship({self.source} -> {self.target})"


    def _determine_relationship_type(self):
        if self.source.is_primary_key and self.target.is_foreign_key:
            return "OneToMany"
        elif self.source.is_foreign_key and self.target.is_primary_key:
            return "ManyToOne"
        elif self.source.is_foreign_key and self.target.is_foreign_key:
            return "ManyToMany"
        return "Unknown"

# - - - - - - - - - - SCHEMA CONVERSION - - - - - - - - - - 

class SchemaConverter:
    
    def convert(self, schema) -> Tuple[List[Table], List[Relationship]]:
        raise NotImplementedError


class SQLAlchemySchemaConverter(SchemaConverter):

    def convert(self, metadata) -> Tuple[List[Table], List[Relationship]]:
        """
        Convert an SQLAlchemy MetaData object to a list of Schemanyd Table and Relationship objects.

        metadata is an instance of SQLAlchemy MetaData.
        sqla_... prefix is used for local variables that hold SQLAlchemy objects.
        """
        
        if not hasattr(metadata, "tables"):
            raise TypeError("SQLAlchemy converter expects a MetaData-like object with a 'tables' attribute.")

        # Mappings for tables and columns
        table_lookup: Dict[str, Table] = {}

        # These are the final nodes and edges of the graph
        tables: List[Table] = []  # nodes
        relationships: List[Relationship] = []  # edges

        # 1st Pass: Create Tables with Columns | without Relationships and Arguments (Constraints / Indexes)
        for table_name, sqla_table in metadata.tables.items():  # Iterate SQLAlchemy Table objects (and create Schemanyd Table objects)
            table_obj = Table(name=table_name)
            tables.append(table_obj)
            table_lookup[table_name] = table_obj  # local lookup to get table objects by name | columns can be looked up by Table.get_column_by_name()

            for sqla_column in sqla_table.columns:  # Iterate SQLAlchemy Column objects (and create Schemanyd Column objects)

                column_obj = Column(
                    table=table_obj,
                    name=sqla_column.name,
                    data_type=str(sqla_column.type),
                    is_primary_key=bool(sqla_column.primary_key),
                    is_foreign_key=bool(sqla_column.foreign_keys),
                )
                table_obj.add_column(column_obj)

                # - - - - - Column-based Argument Conversion - - - - -
                # The arguments won't be added to the columns here, but later all arguments (also those which might apply to multiple columns) will be added to their respective columns.
                # - - - NotNullConstraint - - -
                if not sqla_column.nullable:
                    table_obj.add_argument(NotNullConstraint(
                        table=table_obj,
                        column=column_obj
                    ))

                # - - - DefaultConstraint - - -
                if sqla_column.default is not None:
                    table_obj.add_argument(DefaultConstraint(
                        table=table_obj,
                        column=column_obj,
                        default=sqla_column.default
                    ))

        # 2nd Pass: Inspect table objects again and create arguments (Foreign Keys needs the other Table Objects to be created, therefore this is done in a second round)
        for table_name, sqla_table in metadata.tables.items():

            table_obj = table_lookup.get(table_name)

            # - - - - - Table-based Argument Conversion - - - - -
            # - - - Index - - -
            for sqla_index in sqla_table.indexes:
                table_obj.add_argument(Index(
                    table=table_obj,
                    columns=[table_obj.get_column_by_name(col.name) for col in sqla_index.columns],
                    name=sqla_index.name
                ))
                
            # - - - - - Constraints (Foreign Key, Primary Key, Unique, Check) - - - - -
            for sqla_constraint in sqla_table.constraints:

                # - - - Foreign Key - - -
                if isinstance(sqla_constraint, SQLA_ForeignKeyConstraint):
                    
                    referenced_table = table_lookup.get(sqla_constraint.referred_table.name)  # Get the referenced table
                    referenced_columns = [referenced_table.get_column_by_name(fk.column.name) for fk in sqla_constraint.elements]  # Extract referenced columns from ForeignKey elements, each element is a ForeignKey object with a .column attribute pointing to the target column
                    
                    table_obj.add_argument(ForeignKeyConstraint(
                        table=table_obj,
                        columns=[table_obj.get_column_by_name(col.name) for col in sqla_constraint.columns],
                        referenced_table=referenced_table,
                        referenced_columns=referenced_columns,
                        name=sqla_constraint.name
                    ))

                # - - - Primary Key - - -
                if isinstance(sqla_constraint, SQLA_PrimaryKeyConstraint):
                    table_obj.add_argument(PrimaryKeyConstraint(  # Maybe implement a check later which prevents duplicate primary keys
                        table=table_obj,
                        columns=[table_obj.get_column_by_name(col.name) for col in sqla_table.primary_key.columns],
                        name=sqla_table.primary_key.name
                    ))

                # - - - Unique - - -
                if isinstance(sqla_constraint, SQLA_UniqueConstraint):
                    table_obj.add_argument(UniqueConstraint(
                        table=table_obj,
                        columns=[table_obj.get_column_by_name(col.name) for col in sqla_constraint.columns],
                        name=sqla_constraint.name
                    ))

                # - - - Check - - -
                if isinstance(sqla_constraint, SQLA_CheckConstraint):
                    table_obj.add_argument(CheckConstraint(
                        table=table_obj,
                        columns=[table_obj.get_column_by_name(col.name) for col in sqla_constraint.columns],
                        condition=sqla_constraint.expression,
                        name=sqla_constraint.name
                    ))

            # At the end of the second path, all table arguments have been added to their respective columns and will now be...
            # ...added to the columns they affect
            
            for argument in table_obj.arguments:
                if isinstance(argument, (Index, TableConstraint)):
                    for col in argument.columns:
                        col.add_argument(argument)
                elif isinstance(argument, ColumnConstraint):
                    argument.column.add_argument(argument)
                else:
                    print(f"Unhandled argument type: {type(argument)}")  # This should never be reached

            # ...checked for relations to create Relationship Objects

            for argument in table_obj.arguments:
                
                if not isinstance(argument, ForeignKeyConstraint):
                    continue

                if len(argument.columns) != 1 and len(argument.referenced_columns) != 1:
                    raise ValueError("Schemanyd is not able to handle composite foreign keys yet. Unfortunately, you would need to adjust your schema to utilize Schemanyd.")  # Maybe add a feature to ignore some tables and use Schemanyd on a subset of the database

                source_column = argument.table.get_column_by_name(argument.columns[0].name)
                target_column = argument.referenced_table.get_column_by_name(argument.referenced_columns[0].name)

                # Create the Relationship from the local (source) to the referenced (target) column
                relationship = Relationship(source=source_column, target=target_column)
                relationships.append(relationship)
                source_column.table.add_relationship(relationship)
                target_column.table.add_relationship(relationship)

        return tables, relationships

# - - - - - REGISTER CONVERTERS - - - - -

register_converters()