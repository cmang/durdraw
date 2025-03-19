# Search the plugin directories for plugins to load, and load them
# Look in ~/.durdraw/plugins and {durdraw}/plugins/
# plugin {
#   name: "My Plugin",
#   path: "/path/to/file.py",
#   provides: ["transform_frame", "transform_video"],
# }

# plugin_list = { }

import os
import importlib.util

class DurPlugin:
    def __init__(self):
        #self.plugin_dirs = ["./plugins", "~/.durdraw/plugins"]
        self.plugin_dirs = ["~/.durdraw/plugins"]
        self.loaded_plugins = self.load_plugins(self.plugin_dirs)

    def load_plugins(self, directories):
        plugins = {}

        for directory in directories:
            directory = os.path.expanduser(directory)
            if os.path.isdir(directory) and os.access(directory, os.R_OK):
                # List all .py files in the directory
                for filename in os.listdir(directory):
                    if filename.endswith(".py"):
                        file_path = os.path.join(directory, filename)
                        module_name = filename[:-3]  # Strip '.py' from the filename

                        # Dynamically load the module
                        spec = importlib.util.spec_from_file_location(module_name, file_path)
                        if spec:
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            
                            # Check if the module contains a 'durdraw_plugin' dict
                            if hasattr(module, 'durdraw_plugin') and isinstance(module.durdraw_plugin, dict):
                                plugins[module_name] = {
                                    "meta": module.durdraw_plugin,
                                    "module": module,  # Store the module for execution
                                    "path": file_path,   # path to .py file for dynamic reloading
                                    "module_name": module_name
                                }
            else:
                print(f"Could not read path: {directory}")
                print(f"isdir: {os.path.isdir(directory)},  access: {os.access(directory, os.R_OK)}")
        return plugins

    def run_plugin_transform_frame(self, plugin_name, frame, ui=None):
        if plugin_name in self.loaded_plugins:
            self.reload_plugin(plugin_name)
            plugin = self.loaded_plugins[plugin_name]
            if "transform_frame" in plugin["meta"]["provides"]:
                if ui:
                    ui.undo.push()
                return plugin["module"].transform_frame(frame, appState=ui.appState)
        raise ValueError(f"Plugin '{plugin_name}' not found or doesn't provide transform_frame")

    def run_plugin_transform_mov(self, plugin_name, mov, ui=None):
        if plugin_name in self.loaded_plugins:
            self.reload_plugin(plugin_name)
            plugin = self.loaded_plugins[plugin_name]
            if "transform_movie" in plugin["meta"]["provides"]:
                if ui:
                    ui.undo.push()
                mov = plugin["module"].transform_movie(mov, appState=ui.appState)
                if ui:
                    ui.setPlaybackRange(1, mov.frameCount)
                return mov
        raise ValueError(f"Plugin '{plugin_name}' not found or doesn't provide transform_movie")

    def reload_plugin(self, plugin_name):
        file_path = self.loaded_plugins[plugin_name]["path"]
        module_name = self.loaded_plugins[plugin_name]["module_name"]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check if the module contains a 'durdraw_plugin' dict
            if hasattr(module, 'durdraw_plugin') and isinstance(module.durdraw_plugin, dict):
                self.loaded_plugins[module_name] = {
                    "meta": module.durdraw_plugin,
                    "module": module,  # Store the module for execution
                    "path": file_path,   # path to .py file for dynamic reloading
                    "module_name": module_name
                }


if __name__ == "__main__":
    # Example usage:
    #plugin_dirs = ["./plugins_dir"]
    #plugin_dirs = ["~/.durdraw/plugins", "./plugins"]
    plugin_system = DurPlugin()
    print(f"Loading plugins from {plugin_system.plugin_dirs}")
    loaded_plugins = plugin_system.loaded_plugins
    print("Loaded plugins:")
    for plugin_name, plugin in loaded_plugins.items():
        print(f"{plugin_name}, content: {plugin}")


