from typing import List, Set, Dict, Tuple, TYPE_CHECKING, Any
from collections import deque

# Avoid circular imports: only import graph types for type checking.
if TYPE_CHECKING:
    from ..graph import Graph, Table, Relationship  # pragma: no cover - typing only
else:
    # At runtime we don't need the actual classes for duck-typed operations; use Any placeholders
    Graph = Any  # type: ignore
    Table = Any  # type: ignore
    Relationship = Any  # type: ignore

# DISCLAIMER
# These visualizations were created by AI and may not be accurate in all cases. Please keep that in mind.

def draw_visualizations(graph: Graph, style: List[str]) -> str:
    """
    Generate a string representation of the graph structure for visualization.

    Parameters
    ----------
    graph: Graph
        The Schemanyd Graph object to visualize.
    style: List[str]
        List of visualization styles to apply. Multiple styles can be combined.
        
        Available Styles:
        -----------------
        
        **All**
        - Use ["all"] to apply all available styles in a stable order.

        **Basic Styles:**
        
        - "simple": Simple list of tables and their relationships
        - "detailed": Detailed view with columns, types, and constraints
        - "compact": Minimal one-line per table summary
        
        **Relationship-Focused Styles:**
        
        - "relations": Focus on table relationships with directional arrows
        - "hierarchy": Tree-like view showing parent-child relationships
        - "dependency_chain": Shows the full dependency chain from each table
        - "bidirectional": Shows both incoming and outgoing relationships separately
        
        **Exploration Styles:**
        
        - "explorer": Interactive exploration showing paths from a starting point
        - "full_paths": Explores all possible paths through the database
        - "depth_first": Depth-first traversal showing full database structure
        - "breadth_first": Breadth-first traversal showing database layers
        
        **Analytical Styles:**
        
        - "stats": Statistical overview of the database structure
        - "complexity": Shows complexity metrics for each table
        - "centrality": Identifies central/hub tables in the schema
        - "isolated": Shows tables with no or few relationships
        
        **Visual Styles:**
        
        - "ascii_graph": ASCII art graph representation
        - "tree": Tree-like ASCII structure
        - "boxed": Tables in ASCII boxes with connections
        - "mermaid": Mermaid.js compatible diagram format
        
        **Constraint Styles:**
        
        - "constraints": Focus on constraints (PK, FK, UNIQUE, etc.)
        - "indexes": Show all indexes in the database
        - "primary_keys": Highlight primary key structures
        - "foreign_keys": Detailed foreign key relationships
        
        **Advanced Styles:**
        
        - "circular_deps": Detect and show circular dependencies
        - "orphans": Show tables with no relationships
        - "network_map": Network-style overview of table connections
        - "path_finder": Find all paths between two tables (requires table names in style list)

    Returns
    -------
    str
        Formatted string representation of the graph according to the selected style(s).
        
    Examples
    --------
    >>> print_graph(graph, ["simple"])
    >>> print_graph(graph, ["detailed", "stats"])
    >>> print_graph(graph, ["hierarchy", "boxed"])
    >>> print_graph(graph, ["full_paths", "explorer"])
    """
    
    if not style:
        style = ["simple"]

    # Supported styles in a stable order. Keep this list in sync with the handlers below.
    supported_styles = [
        "simple", "detailed", "compact", "relations", "hierarchy", "dependency_chain",
        "bidirectional", "explorer", "full_paths", "depth_first", "breadth_first",
        "stats", "complexity", "centrality", "isolated", "ascii_graph", "tree",
        "boxed", "mermaid", "constraints", "indexes", "primary_keys", "foreign_keys",
        "circular_deps", "orphans", "network_map", "path_finder",
    ]

    # If "all" is requested, expand to all supported styles (preserve order and dedupe)
    requested = []
    if "all" in style:
        for s in supported_styles:
            if s not in requested:
                requested.append(s)
    else:
        for s in style:
            if s not in requested:
                requested.append(s)

    outputs = []
    
    for s in requested:
        if s == "simple":
            outputs.append(_style_simple(graph))
        elif s == "detailed":
            outputs.append(_style_detailed(graph))
        elif s == "compact":
            outputs.append(_style_compact(graph))
        elif s == "relations":
            outputs.append(_style_relations(graph))
        elif s == "hierarchy":
            outputs.append(_style_hierarchy(graph))
        elif s == "dependency_chain":
            outputs.append(_style_dependency_chain(graph))
        elif s == "bidirectional":
            outputs.append(_style_bidirectional(graph))
        elif s == "explorer":
            outputs.append(_style_explorer(graph))
        elif s == "full_paths":
            outputs.append(_style_full_paths(graph))
        elif s == "depth_first":
            outputs.append(_style_depth_first(graph))
        elif s == "breadth_first":
            outputs.append(_style_breadth_first(graph))
        elif s == "stats":
            outputs.append(_style_stats(graph))
        elif s == "complexity":
            outputs.append(_style_complexity(graph))
        elif s == "centrality":
            outputs.append(_style_centrality(graph))
        elif s == "isolated":
            outputs.append(_style_isolated(graph))
        elif s == "ascii_graph":
            outputs.append(_style_ascii_graph(graph))
        elif s == "tree":
            outputs.append(_style_tree(graph))
        elif s == "boxed":
            outputs.append(_style_boxed(graph))
        elif s == "mermaid":
            outputs.append(_style_mermaid(graph))
        elif s == "constraints":
            outputs.append(_style_constraints(graph))
        elif s == "indexes":
            outputs.append(_style_indexes(graph))
        elif s == "primary_keys":
            outputs.append(_style_primary_keys(graph))
        elif s == "foreign_keys":
            outputs.append(_style_foreign_keys(graph))
        elif s == "circular_deps":
            outputs.append(_style_circular_deps(graph))
        elif s == "orphans":
            outputs.append(_style_orphans(graph))
        elif s == "network_map":
            outputs.append(_style_network_map(graph))
        elif s == "path_finder":
            outputs.append(_style_path_finder(graph))
        else:
            outputs.append(f"Unknown style: {s}")
    
    return "\n\n" + "="*80 + "\n\n".join(outputs)


# ==================== BASIC STYLES ====================

def _style_simple(graph: Graph) -> str:
    """Simple list of tables and their relationships."""
    lines = ["📊 SIMPLE DATABASE OVERVIEW", "=" * 60, ""]
    
    for table in graph.nodes:
        lines.append(f"📋 Table: {table.name}")
        lines.append(f"   Columns: {len(table.columns)}")
        
        if table.relationships:
            lines.append(f"   Relationships:")
            for rel in table.relationships:
                if rel.source.table == table:
                    lines.append(f"      → {rel.target.table.name} (via {rel.source.name})")
        lines.append("")
    
    return "\n".join(lines)


def _style_detailed(graph: Graph) -> str:
    """Detailed view with columns, types, and constraints."""
    lines = ["📚 DETAILED DATABASE STRUCTURE", "=" * 60, ""]
    
    for table in graph.nodes:
        lines.append(f"╔{'═' * 58}╗")
        lines.append(f"║ 📋 TABLE: {table.name:<47}║")
        lines.append(f"╠{'═' * 58}╣")
        
        lines.append(f"║ COLUMNS:{' ' * 50}║")
        for col_name, col in table.columns.items():
            pk = "🔑" if col.is_primary_key else "  "
            fk = "🔗" if col.is_foreign_key else "  "
            null = "✓" if col.nullable else "✗"
            lines.append(f"║   {pk}{fk} {col.name:<20} {col.data_type:<15} NULL:{null} ║")
        
        if table.arguments:
            lines.append(f"║{' ' * 58}║")
            lines.append(f"║ CONSTRAINTS:{' ' * 46}║")
            for arg in table.arguments:
                arg_type = arg.__class__.__name__
                lines.append(f"║   • {arg_type:<52}║")
        
        lines.append(f"╚{'═' * 58}╝")
        lines.append("")
    
    return "\n".join(lines)


def _style_compact(graph: Graph) -> str:
    """Minimal one-line per table summary."""
    lines = ["📝 COMPACT VIEW", "=" * 60, ""]
    
    for table in graph.nodes:
        rel_count = len(table.relationships)
        col_count = len(table.columns)
        lines.append(f"{table.name:<30} │ {col_count:>2} cols │ {rel_count:>2} rels")
    
    return "\n".join(lines)


# ==================== RELATIONSHIP-FOCUSED STYLES ====================

def _style_relations(graph: Graph) -> str:
    """Focus on table relationships with directional arrows."""
    lines = ["🔗 RELATIONSHIP MAP", "=" * 60, ""]
    
    processed = set()
    for rel in graph.edges:
        rel_key = (rel.source.table.name, rel.target.table.name, rel.source.name)
        if rel_key not in processed:
            lines.append(f"{rel.source.table.name:>30} ─[{rel.source.name}]→ {rel.target.table.name}")
            lines.append(f"{'':>30}   ({rel.relationship_type})")
            processed.add(rel_key)
    
    return "\n".join(lines)


def _style_hierarchy(graph: Graph) -> str:
    """Tree-like view showing parent-child relationships."""
    lines = ["🌲 HIERARCHICAL VIEW", "=" * 60, ""]
    
    # Find root tables (tables that are only referenced, not referencing)
    all_tables = {table.name: table for table in graph.nodes}
    referenced_tables = set()
    referencing_tables = set()
    
    for rel in graph.edges:
        referencing_tables.add(rel.source.table.name)
        referenced_tables.add(rel.target.table.name)
    
    roots = [t for t in all_tables.keys() if t not in referencing_tables or t in referenced_tables]
    
    visited = set()
    
    def print_tree(table_name: str, indent: int = 0, prefix: str = ""):
        if table_name in visited:
            lines.append(f"{prefix}↻ {table_name} (circular reference)")
            return
        
        visited.add(table_name)
        lines.append(f"{prefix}📁 {table_name}")
        
        table = all_tables[table_name]
        children = []
        for rel in table.relationships:
            if rel.source.table.name == table_name:
                children.append(rel.target.table.name)
        
        for i, child in enumerate(children):
            is_last = i == len(children) - 1
            new_prefix = prefix + ("    " if is_last else "│   ")
            branch = "└── " if is_last else "├── "
            print_tree(child, indent + 1, prefix + branch)
    
    for root in sorted(roots):
        print_tree(root)
        lines.append("")
    
    return "\n".join(lines)


def _style_dependency_chain(graph: Graph) -> str:
    """Shows the full dependency chain from each table."""
    lines = ["⛓️  DEPENDENCY CHAINS", "=" * 60, ""]
    
    def get_dependencies(table: Table, visited: Set[str] = None) -> List[str]:
        if visited is None:
            visited = set()
        
        if table.name in visited:
            return [f"↻{table.name}"]
        
        visited.add(table.name)
        deps = []
        
        for rel in table.relationships:
            if rel.source.table == table:
                target = rel.target.table
                sub_deps = get_dependencies(target, visited.copy())
                for sub in sub_deps:
                    deps.append(f"{target.name} → {sub}" if sub != target.name else target.name)
                if not sub_deps:
                    deps.append(target.name)
        
        return deps if deps else [table.name]
    
    for table in graph.nodes:
        lines.append(f"\n🔸 {table.name}:")
        deps = get_dependencies(table)
        for dep in set(deps):
            lines.append(f"   └─→ {dep}")
    
    return "\n".join(lines)


def _style_bidirectional(graph: Graph) -> str:
    """Shows both incoming and outgoing relationships separately."""
    lines = ["↔️  BIDIRECTIONAL RELATIONSHIPS", "=" * 60, ""]
    
    for table in graph.nodes:
        outgoing = []
        incoming = []
        
        for rel in table.relationships:
            if rel.source.table == table:
                outgoing.append(f"{rel.target.table.name} (via {rel.source.name})")
            if rel.target.table == table:
                incoming.append(f"{rel.source.table.name} (via {rel.source.name})")
        
        lines.append(f"\n📊 {table.name}")
        
        if outgoing:
            lines.append(f"   ⬆️  Outgoing ({len(outgoing)}):")
            for out in outgoing:
                lines.append(f"      → {out}")
        
        if incoming:
            lines.append(f"   ⬇️  Incoming ({len(incoming)}):")
            for inc in incoming:
                lines.append(f"      ← {inc}")
        
        if not outgoing and not incoming:
            lines.append("   🔵 No relationships")
    
    return "\n".join(lines)


# ==================== EXPLORATION STYLES ====================

def _style_explorer(graph: Graph) -> str:
    """Interactive exploration showing paths from starting points."""
    lines = ["🧭 DATABASE EXPLORER", "=" * 60, ""]
    
    # Pick tables with most relationships as starting points
    sorted_tables = sorted(graph.nodes, key=lambda t: len(t.relationships), reverse=True)
    starting_points = sorted_tables[:3]
    
    for start_table in starting_points:
        lines.append(f"\n🎯 Starting from: {start_table.name}")
        visited = set()
        queue = deque([(start_table, 0, [])])
        
        while queue:
            table, depth, path = queue.popleft()
            
            if table.name in visited or depth > 3:
                continue
            
            visited.add(table.name)
            indent = "  " * depth
            path_str = " → ".join(path + [table.name])
            lines.append(f"{indent}{'└─' if depth > 0 else ''}🔹 {table.name} (path: {path_str})")
            
            for rel in table.relationships:
                if rel.source.table == table:
                    queue.append((rel.target.table, depth + 1, path + [table.name]))
    
    return "\n".join(lines)


def _style_full_paths(graph: Graph) -> str:
    """Explores all possible paths through the database."""
    lines = ["🗺️  ALL DATABASE PATHS", "=" * 60, ""]
    
    def find_all_paths(start: Table, max_depth: int = 4) -> List[List[str]]:
        paths = []
        
        def dfs(current: Table, path: List[str], visited: Set[str]):
            if len(path) > max_depth:
                return
            
            if current.name in visited:
                paths.append(path + [f"↻{current.name}"])
                return
            
            new_visited = visited.copy()
            new_visited.add(current.name)
            new_path = path + [current.name]
            
            has_children = False
            for rel in current.relationships:
                if rel.source.table == current:
                    has_children = True
                    dfs(rel.target.table, new_path, new_visited)
            
            if not has_children:
                paths.append(new_path)
        
        dfs(start, [], set())
        return paths
    
    for table in graph.nodes[:5]:  # Limit to first 5 tables to avoid overwhelming output
        lines.append(f"\n📍 Paths from {table.name}:")
        paths = find_all_paths(table)
        for i, path in enumerate(paths[:10], 1):  # Show first 10 paths
            lines.append(f"   {i}. {' → '.join(path)}")
        if len(paths) > 10:
            lines.append(f"   ... and {len(paths) - 10} more paths")
    
    return "\n".join(lines)


def _style_depth_first(graph: Graph) -> str:
    """Depth-first traversal showing full database structure."""
    lines = ["🔍 DEPTH-FIRST TRAVERSAL", "=" * 60, ""]
    
    visited = set()
    
    def dfs(table: Table, depth: int = 0):
        if table.name in visited:
            lines.append(f"{'  ' * depth}↻ {table.name}")
            return
        
        visited.add(table.name)
        lines.append(f"{'  ' * depth}{'└─ ' if depth > 0 else ''}📦 {table.name} ({len(table.columns)} columns)")
        
        for rel in table.relationships:
            if rel.source.table == table:
                dfs(rel.target.table, depth + 1)
    
    for table in graph.nodes:
        if table.name not in visited:
            dfs(table)
            lines.append("")
    
    return "\n".join(lines)


def _style_breadth_first(graph: Graph) -> str:
    """Breadth-first traversal showing database layers."""
    lines = ["📊 BREADTH-FIRST TRAVERSAL (Layers)", "=" * 60, ""]
    
    # Find root tables
    referencing = set()
    for rel in graph.edges:
        referencing.add(rel.source.table.name)
    
    roots = [t for t in graph.nodes if t.name not in referencing]
    if not roots:
        roots = [graph.nodes[0]] if graph.nodes else []
    
    visited = set()
    queue = deque([(table, 0) for table in roots])
    current_level = -1
    
    while queue:
        table, level = queue.popleft()
        
        if table.name in visited:
            continue
        
        visited.add(table.name)
        
        if level != current_level:
            current_level = level
            lines.append(f"\n🔹 LEVEL {level}:")
        
        lines.append(f"   • {table.name} ({len(table.relationships)} relationships)")
        
        for rel in table.relationships:
            if rel.source.table == table:
                queue.append((rel.target.table, level + 1))
    
    return "\n".join(lines)


# ==================== ANALYTICAL STYLES ====================

def _style_stats(graph: Graph) -> str:
    """Statistical overview of the database structure."""
    lines = ["📈 DATABASE STATISTICS", "=" * 60, ""]
    
    total_tables = len(graph.nodes)
    total_relationships = len(graph.edges)
    total_columns = sum(len(t.columns) for t in graph.nodes)
    
    lines.append(f"📊 Overview:")
    lines.append(f"   Tables: {total_tables}")
    lines.append(f"   Relationships: {total_relationships}")
    lines.append(f"   Columns: {total_columns}")
    lines.append(f"   Avg columns per table: {total_columns / max(total_tables, 1):.1f}")
    lines.append(f"   Avg relationships per table: {total_relationships / max(total_tables, 1):.1f}")
    
    lines.append(f"\n🔗 Relationship Distribution:")
    rel_counts = {}
    for table in graph.nodes:
        count = len(table.relationships)
        rel_counts[count] = rel_counts.get(count, 0) + 1
    
    for count in sorted(rel_counts.keys()):
        bar = "█" * rel_counts[count]
        lines.append(f"   {count:>2} relationships: {bar} ({rel_counts[count]} tables)")
    
    lines.append(f"\n📏 Column Distribution:")
    col_counts = {}
    for table in graph.nodes:
        count = len(table.columns)
        col_counts[count] = col_counts.get(count, 0) + 1
    
    for count in sorted(col_counts.keys())[:10]:  # Show top 10
        bar = "█" * col_counts[count]
        lines.append(f"   {count:>2} columns: {bar} ({col_counts[count]} tables)")
    
    return "\n".join(lines)


def _style_complexity(graph: Graph) -> str:
    """Shows complexity metrics for each table."""
    lines = ["🧮 TABLE COMPLEXITY ANALYSIS", "=" * 60, ""]
    
    complexity_scores = []
    
    for table in graph.nodes:
        # Calculate complexity score
        col_score = len(table.columns) * 1
        rel_score = len(table.relationships) * 2
        constraint_score = len(table.arguments) * 1.5
        total_score = col_score + rel_score + constraint_score
        
        complexity_scores.append((table.name, total_score, len(table.columns), 
                                  len(table.relationships), len(table.arguments)))
    
    complexity_scores.sort(key=lambda x: x[1], reverse=True)
    
    lines.append(f"{'Table':<30} │ Score │ Cols │ Rels │ Constraints")
    lines.append("─" * 70)
    
    for name, score, cols, rels, constraints in complexity_scores:
        complexity = "🔴" if score > 50 else "🟡" if score > 30 else "🟢"
        lines.append(f"{name:<30} │ {complexity} {score:>3.0f} │ {cols:>4} │ {rels:>4} │ {constraints:>11}")
    
    return "\n".join(lines)


def _style_centrality(graph: Graph) -> str:
    """Identifies central/hub tables in the schema."""
    lines = ["🎯 TABLE CENTRALITY ANALYSIS", "=" * 60, ""]
    
    # Calculate centrality based on incoming and outgoing relationships
    centrality = {}
    
    for table in graph.nodes:
        incoming = sum(1 for rel in table.relationships if rel.target.table == table)
        outgoing = sum(1 for rel in table.relationships if rel.source.table == table)
        total = incoming + outgoing
        centrality[table.name] = (total, incoming, outgoing)
    
    sorted_centrality = sorted(centrality.items(), key=lambda x: x[1][0], reverse=True)
    
    lines.append(f"{'Table':<30} │ Total │ In  │ Out │ Role")
    lines.append("─" * 70)
    
    for name, (total, incoming, outgoing) in sorted_centrality:
        if total > 5:
            role = "🌟 HUB"
        elif incoming > outgoing * 2:
            role = "📥 SINK"
        elif outgoing > incoming * 2:
            role = "📤 SOURCE"
        elif total == 0:
            role = "🔵 ISOLATED"
        else:
            role = "🔷 NORMAL"
        
        lines.append(f"{name:<30} │ {total:>5} │ {incoming:>3} │ {outgoing:>3} │ {role}")
    
    return "\n".join(lines)


def _style_isolated(graph: Graph) -> str:
    """Shows tables with no or few relationships."""
    lines = ["🏝️  ISOLATED TABLES", "=" * 60, ""]
    
    isolated = []
    few_rels = []
    
    for table in graph.nodes:
        rel_count = len(table.relationships)
        if rel_count == 0:
            isolated.append(table.name)
        elif rel_count <= 2:
            few_rels.append((table.name, rel_count))
    
    if isolated:
        lines.append(f"\n🔴 Completely Isolated ({len(isolated)}):")
        for name in isolated:
            lines.append(f"   • {name}")
    
    if few_rels:
        lines.append(f"\n🟡 Few Relationships ({len(few_rels)}):")
        for name, count in few_rels:
            lines.append(f"   • {name} ({count} relationship{'s' if count > 1 else ''})")
    
    if not isolated and not few_rels:
        lines.append("\n✅ All tables are well connected!")
    
    return "\n".join(lines)


# ==================== VISUAL STYLES ====================

def _style_ascii_graph(graph: Graph) -> str:
    """ASCII art graph representation."""
    lines = ["🎨 ASCII GRAPH", "=" * 60, ""]
    
    for table in graph.nodes:
        lines.append(f"\n    ╔═══════════════╗")
        lines.append(f"    ║ {table.name:<13} ║")
        lines.append(f"    ╚═══════════════╝")
        
        for rel in table.relationships:
            if rel.source.table == table:
                lines.append(f"           │")
                lines.append(f"           │ {rel.source.name}")
                lines.append(f"           ↓")
                lines.append(f"    ┌──────────────┐")
                lines.append(f"    │ {rel.target.table.name:<12} │")
                lines.append(f"    └──────────────┘")
    
    return "\n".join(lines)


def _style_tree(graph: Graph) -> str:
    """Tree-like ASCII structure."""
    lines = ["🌳 TREE STRUCTURE", "=" * 60, ""]
    
    visited = set()
    
    def print_node(table: Table, prefix: str = "", is_last: bool = True):
        if table.name in visited:
            lines.append(f"{prefix}{'└── ' if is_last else '├── '}↻ {table.name}")
            return
        
        visited.add(table.name)
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}📦 {table.name}")
        
        children = [rel.target.table for rel in table.relationships if rel.source.table == table]
        
        for i, child in enumerate(children):
            extension = "    " if is_last else "│   "
            print_node(child, prefix + extension, i == len(children) - 1)
    
    for table in graph.nodes:
        if table.name not in visited:
            print_node(table)
    
    return "\n".join(lines)


def _style_boxed(graph: Graph) -> str:
    """Tables in ASCII boxes with connections."""
    lines = ["📦 BOXED VIEW", "=" * 60, ""]
    
    for table in graph.nodes:
        box_width = max(40, len(table.name) + 4)
        
        lines.append(f"\n┏{'━' * (box_width - 2)}┓")
        lines.append(f"┃ 📋 {table.name:<{box_width - 6}}┃")
        lines.append(f"┣{'━' * (box_width - 2)}┫")
        
        for col_name, col in list(table.columns.items())[:5]:  # Show first 5 columns
            marker = "🔑" if col.is_primary_key else "🔗" if col.is_foreign_key else "  "
            lines.append(f"┃ {marker} {col_name:<{box_width - 7}}┃")
        
        if len(table.columns) > 5:
            lines.append(f"┃ ... and {len(table.columns) - 5} more columns{' ' * (box_width - 30)}┃")
        
        lines.append(f"┗{'━' * (box_width - 2)}┛")
        
        # Show connections
        for rel in table.relationships[:3]:  # Show first 3 relationships
            if rel.source.table == table:
                lines.append(f"      ║")
                lines.append(f"      ╚══[{rel.source.name}]═══> {rel.target.table.name}")
    
    return "\n".join(lines)


def _style_mermaid(graph: Graph) -> str:
    """Mermaid.js compatible diagram format."""
    lines = ["🎭 MERMAID DIAGRAM", "=" * 60, ""]
    lines.append("```mermaid")
    lines.append("erDiagram")
    
    for table in graph.nodes:
        # Define table with columns
        for col_name, col in table.columns.items():
            col_type = col.data_type.replace(" ", "_")
            pk = " PK" if col.is_primary_key else ""
            fk = " FK" if col.is_foreign_key else ""
            lines.append(f"    {table.name} {{")
            lines.append(f"        {col_type} {col_name}{pk}{fk}")
            lines.append(f"    }}")
            break  # Just show structure, mermaid will handle the rest
    
    # Add relationships
    processed = set()
    for rel in graph.edges:
        rel_key = (rel.source.table.name, rel.target.table.name)
        if rel_key not in processed:
            # Determine relationship cardinality
            if rel.relationship_type == "OneToMany":
                connector = "||--o{"
            elif rel.relationship_type == "ManyToOne":
                connector = "}o--||"
            else:
                connector = "||--||"
            
            lines.append(f"    {rel.source.table.name} {connector} {rel.target.table.name} : \"{rel.source.name}\"")
            processed.add(rel_key)
    
    lines.append("```")
    
    return "\n".join(lines)


# ==================== CONSTRAINT STYLES ====================

def _style_constraints(graph: Graph) -> str:
    """Focus on constraints (PK, FK, UNIQUE, etc.)."""
    lines = ["🔒 CONSTRAINT OVERVIEW", "=" * 60, ""]
    
    for table in graph.nodes:
        if not table.arguments:
            continue
        
        lines.append(f"\n📋 {table.name}:")
        
        for arg in table.arguments:
            arg_type = arg.__class__.__name__
            
            if hasattr(arg, 'columns') and arg.columns:
                col_names = ", ".join([c.name for c in arg.columns])
                lines.append(f"   🔹 {arg_type}: {col_names}")
            else:
                lines.append(f"   🔹 {arg_type}")
    
    return "\n".join(lines)


def _style_indexes(graph: Graph) -> str:
    """Show all indexes in the database."""
    lines = ["📇 INDEX OVERVIEW", "=" * 60, ""]
    
    total_indexes = 0
    
    for table in graph.nodes:
        indexes = [arg for arg in table.arguments if arg.__class__.__name__ == "Index"]
        
        if indexes:
            lines.append(f"\n📋 {table.name}:")
            for idx in indexes:
                total_indexes += 1
                col_names = ", ".join([c.name for c in idx.columns]) if hasattr(idx, 'columns') else "N/A"
                idx_name = idx.name if hasattr(idx, 'name') and idx.name else "unnamed"
                lines.append(f"   🔹 {idx_name}: ({col_names})")
    
    lines.insert(2, f"\nTotal Indexes: {total_indexes}\n")
    
    return "\n".join(lines)


def _style_primary_keys(graph: Graph) -> str:
    """Highlight primary key structures."""
    lines = ["🔑 PRIMARY KEY OVERVIEW", "=" * 60, ""]
    
    for table in graph.nodes:
        pk_cols = [col for col in table.columns.values() if col.is_primary_key]
        
        if pk_cols:
            col_names = ", ".join([col.name for col in pk_cols])
            pk_type = "Composite" if len(pk_cols) > 1 else "Single"
            lines.append(f"🔹 {table.name:<30} │ {pk_type:<10} │ {col_names}")
        else:
            lines.append(f"❌ {table.name:<30} │ No PK")
    
    return "\n".join(lines)


def _style_foreign_keys(graph: Graph) -> str:
    """Detailed foreign key relationships."""
    lines = ["🔗 FOREIGN KEY DETAILS", "=" * 60, ""]
    
    for table in graph.nodes:
        fks = [arg for arg in table.arguments if arg.__class__.__name__ == "ForeignKeyConstraint"]
        
        if fks:
            lines.append(f"\n📋 {table.name}:")
            for fk in fks:
                if hasattr(fk, 'columns') and hasattr(fk, 'referenced_table'):
                    local_cols = ", ".join([c.name for c in fk.columns])
                    ref_cols = ", ".join([c.name for c in fk.referenced_columns]) if hasattr(fk, 'referenced_columns') else "?"
                    lines.append(f"   🔗 {local_cols} → {fk.referenced_table.name}({ref_cols})")
    
    return "\n".join(lines)


# ==================== ADVANCED STYLES ====================

def _style_circular_deps(graph: Graph) -> str:
    """Detect and show circular dependencies."""
    lines = ["🔄 CIRCULAR DEPENDENCY DETECTION", "=" * 60, ""]
    
    def find_cycles():
        cycles = []
        
        def dfs(table: Table, path: List[str], visited: Set[str]):
            if table.name in path:
                cycle_start = path.index(table.name)
                cycles.append(path[cycle_start:] + [table.name])
                return
            
            if table.name in visited:
                return
            
            visited.add(table.name)
            
            for rel in table.relationships:
                if rel.source.table == table:
                    dfs(rel.target.table, path + [table.name], visited.copy())
        
        for table in graph.nodes:
            dfs(table, [], set())
        
        return cycles
    
    cycles = find_cycles()
    
    if cycles:
        lines.append(f"\n⚠️  Found {len(cycles)} circular dependencies:\n")
        for i, cycle in enumerate(cycles, 1):
            lines.append(f"   {i}. {' → '.join(cycle)}")
    else:
        lines.append("\n✅ No circular dependencies detected!")
    
    return "\n".join(lines)


def _style_orphans(graph: Graph) -> str:
    """Show tables with no relationships."""
    lines = ["🏝️  ORPHAN TABLES", "=" * 60, ""]
    
    orphans = [table for table in graph.nodes if len(table.relationships) == 0]
    
    if orphans:
        lines.append(f"\nFound {len(orphans)} orphan table(s):\n")
        for table in orphans:
            lines.append(f"   🔵 {table.name} ({len(table.columns)} columns)")
    else:
        lines.append("\n✅ No orphan tables - all tables are connected!")
    
    return "\n".join(lines)


def _style_network_map(graph: Graph) -> str:
    """Network-style overview of table connections."""
    lines = ["🕸️  NETWORK MAP", "=" * 60, ""]
    
    # Create adjacency representation
    for table in graph.nodes:
        connections = set()
        for rel in table.relationships:
            if rel.source.table == table:
                connections.add(f"→{rel.target.table.name}")
            if rel.target.table == table:
                connections.add(f"←{rel.source.table.name}")
        
        if connections:
            lines.append(f"\n{table.name:^30}")
            lines.append(f"{'─' * 30}")
            for conn in sorted(connections):
                lines.append(f"  {conn}")
        else:
            lines.append(f"\n{table.name} (isolated)")
    
    return "\n".join(lines)


def _style_path_finder(graph: Graph) -> str:
    """Find all paths between tables."""
    lines = ["🛤️  PATH FINDER", "=" * 60, ""]
    
    def find_path(start: Table, end: Table, max_depth: int = 5) -> List[List[str]]:
        paths = []
        
        def dfs(current: Table, target: Table, path: List[str], visited: Set[str]):
            if len(path) > max_depth:
                return
            
            if current == target and len(path) > 0:
                paths.append(path + [current.name])
                return
            
            if current.name in visited:
                return
            
            visited.add(current.name)
            
            for rel in current.relationships:
                if rel.source.table == current:
                    dfs(rel.target.table, target, path + [current.name], visited.copy())
        
        dfs(start, end, [], set())
        return paths
    
    # Find paths between first few tables
    tables = graph.nodes[:3]
    for i, start in enumerate(tables):
        for end in tables[i+1:]:
            paths = find_path(start, end)
            if paths:
                lines.append(f"\n🔍 Paths from {start.name} to {end.name}:")
                for j, path in enumerate(paths[:5], 1):
                    lines.append(f"   {j}. {' → '.join(path)}")
            else:
                lines.append(f"\n❌ No path found between {start.name} and {end.name}")
    
    return "\n".join(lines)
