from types import MappingProxyType
import yaml

def read_config(path: str) -> dict:
    with open(path, "r") as file:
        config = yaml.safe_load(file)
    agents_id_map = MappingProxyType({agent["name"]: agent["id"] for agent in config['agents']})
    query_tags = set(config['tags'])
    return [
        agents_id_map,
        query_tags,
    ]
    