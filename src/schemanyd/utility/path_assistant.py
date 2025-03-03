from collections import deque

from schemanyd.schemanyd import Schemanyd

class PathAssistant:

    def __init__(self, schemanyd: Schemanyd):
        """
        [POTENTIAL ADD] Add refresh function which pulls new data from Schemanyd object after initialization
        """
        self.schemanyd = schemanyd

        self.schema = schemanyd.db.schema
        self.graph = schemanyd.db.graph
        self.seperator_rf = schemanyd.seperator_rf
        self.seperator_rr = schemanyd.seperator_rr

        self.all_tables = set(self.schema.tables.keys())


    async def find_join_path(self, required_tables):
        missing_tables = [table for table in required_tables if table not in self.all_tables]
        if missing_tables:
            print(f"Error: The following required tables were not found in the schema: {missing_tables}")
            return None


    async def get_table_path(self, table_name: str) -> str:
        """
        
        """
        table_info = self.schema.get(table_name)
        if not table_info:
            raise ValueError(f"Table '{table_name}' not found in schema.")
        return table_info.get("path", "")
    

    def find_shortest_path(self, start, end):
        """
        Breadth First Search AlgorithmFind the shortest path between start and end using BFS
        """
        if start == end:
            return [start]
        
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            node, path = queue.popleft()
            
            for neighbor in self.graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [neighbor]
                    
                    if neighbor == end:
                        return new_path
                    
                    queue.append((neighbor, new_path))
        
        return None
