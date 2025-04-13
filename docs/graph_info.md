# Schemanyd Graph | Nodes and Edges

Schemanyd uses the SQLalchemy ORM to obtain MetaData class database schemas. These are then converted to the Schemanyd Graph structure, which consists of nodes (representing database tables) and edges (representing relationships such as foreign keys).

## Edge Examples

### 1:1 (One-to-One) Relationships
to be added

### 1:N (One-to-Many) Relationships
to be added

### M:N (Many-to-Many) Relationships
to be added

## Graph Traversal
Schemanyd should provide various graph traversal capabilities to facilitate complex queries and data retrieval. These include:

### Priority

- **Shortest Path Finding**: Identify the shortest path between any two tables for efficient JOIN generation.
- **Circular Dependency Detection**: Automatically detect circular dependencies and potential infinite loops in the schema.

---

### Planned for future releases


- **Hub Table Identification**: Recognize hub tables that have many connections, which can be critical for query optimization.
- **Query Execution Plan Generation**: Generate optimal query execution plans based on the graph structure.
- **Referential Integrity Validation**: Validate referential integrity constraints across the schema.
- **Documentation Generation**: Auto-generate database documentation and ER diagrams from the graph representation.