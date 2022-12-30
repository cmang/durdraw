from importlib.resources import files

def get_resource_path(module: str, name: str) -> str:
    """Load a resource file."""
    return files(module).joinpath(name)

