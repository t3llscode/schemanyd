# This class is creating a generic representation of the schema,
# allowing for better encapsulation and manipulation of the graph structure.

from email.policy import default
from typing import Dict, List, Tuple, Type

# My Imports
from .table_argument import TableArgument


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
        self.arguemnts: List[TableArgument] = []


    def add_column(self, column: "Column") -> None:
        self.columns[column.name] = column


    def add_relationship(self, relationship: "Relationship") -> None:
        if relationship not in self.relationships:
            self.relationships.append(relationship)


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
        self.arguemnts: List[TableArgument] = []  # not sure if necessary for schemanyd


    def add_arguemnts(self, constraint: TableArgument) -> None:
        if constraint not in self.constraints:
            self.constraints.append(constraint)


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
        
        if not hasattr(metadata, "tables"):
            raise TypeError("SQLAlchemy converter expects a MetaData-like object with a 'tables' attribute.")

        table_nodes: Dict[str, Table] = {}
        column_lookup: Dict[Tuple[str, str], Column] = {}
        nodes: List[Table] = []
        edges: List[Relationship] = []

        for table_name, sa_table in metadata.tables.items():
            table_node = Table(name=table_name)
            table_nodes[table_name] = table_node
            nodes.append(table_node)

            for sa_column in sa_table.columns:
                column_node = Column(
                    table=table_node,
                    name=sa_column.name,
                    data_type=str(sa_column.type),
                    is_primary_key=bool(sa_column.primary_key),
                    is_foreign_key=bool(sa_column.foreign_keys),
                )
                table_node.add_column(column_node)
                column_lookup[(table_name, sa_column.name)] = column_node

        for table_name, sa_table in metadata.tables.items():
            for sa_column in sa_table.columns:
                local_column = column_lookup[(table_name, sa_column.name)]
                for fk in sa_column.foreign_keys:
                    remote_column = fk.column
                    if remote_column is None or remote_column.table is None:
                        continue

                    remote_table_name = remote_column.table.name
                    remote_column_key = (remote_table_name, remote_column.name)
                    source_column = column_lookup.get(remote_column_key)
                    if source_column is None:
                        continue

                    relationship = Relationship(source=source_column, target=local_column)
                    edges.append(relationship)
                    source_column.table.add_relationship(relationship)
                    local_column.table.add_relationship(relationship)

        return nodes, edges

# - - - - - REGISTER CONVERTERS - - - - -

register_converters()
