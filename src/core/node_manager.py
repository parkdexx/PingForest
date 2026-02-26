import json
import os
from typing import Optional, List
from .models import NodeModel, NodeType

class NodeManager:
    def __init__(self, data_file_path: str = "tree_data.json"):
        self.data_file_path = data_file_path
        self.root_nodes: List[NodeModel] = []
        self._all_nodes = {}  # id -> NodeModel for fast lookup
        self.load_data()

    def add_node(self, node: NodeModel, parent_id: Optional[str] = None):
        if parent_id is None:
            self.root_nodes.append(node)
        else:
            parent = self.get_node(parent_id)
            if parent:
                parent.children.append(node)
                node.parent_id = parent_id
            else:
                raise ValueError(f"Parent node {parent_id} not found")
        
        self._register_node_recursive(node)
        self.save_data()

    def _register_node_recursive(self, node: NodeModel):
        self._all_nodes[node.id] = node
        for child in node.children:
            self._register_node_recursive(child)

    def remove_node(self, node_id: str):
        node = self.get_node(node_id)
        if not node:
            return

        if node.parent_id is None:
            self.root_nodes = [n for n in self.root_nodes if n.id != node_id]
        else:
            parent = self.get_node(node.parent_id)
            if parent:
                parent.children = [n for n in parent.children if n.id != node_id]
                
        self._unregister_node_recursive(node)
        self.save_data()

    def _unregister_node_recursive(self, node: NodeModel):
        if node.id in self._all_nodes:
            del self._all_nodes[node.id]
        for child in node.children:
            self._unregister_node_recursive(child)

    def get_node(self, node_id: str) -> Optional[NodeModel]:
        return self._all_nodes.get(node_id)

    def get_all_devices(self) -> List[NodeModel]:
        return [node for node in self._all_nodes.values() if node.type == NodeType.DEVICE]

    def save_data(self):
        data = [node.to_dict() for node in self.root_nodes]
        try:
            with open(self.data_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save tree data: {e}")

    def load_data(self):
        self.root_nodes = []
        self._all_nodes = {}
        if not os.path.exists(self.data_file_path):
            return
            
        try:
            with open(self.data_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item_data in data:
                    node = NodeModel.from_dict(item_data)
                    self.root_nodes.append(node)
                    self._register_node_recursive(node)
        except Exception as e:
            print(f"Failed to load tree data: {e}")
