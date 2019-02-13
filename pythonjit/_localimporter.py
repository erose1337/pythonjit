import sys
import imp

class Local_Importer(object):

    def __init__(self, source_dir):
        self.source_dir = source_dir
        self.source = dict()
        sys.meta_path.append(self)

    def find_module(self, module, path):
        try:
            _file, filepath, _ = imp.find_module(module, [self.source_dir])
        except ImportError:
            pass
        else:
            self.source[module] = _file.read(), filepath
            _file.close()
            return self

    def load_module(self, module_name):
        while imp.lock_held():
            pass
        imp.acquire_lock()
        module = sys.modules.setdefault(module_name, imp.new_module(module_name))
        imp.release_lock() # not sure when to release; the following doesn't use shared resources (e.g. sys.modules) other than the module itself
        source, filepath = self.source.pop(module_name)
        module_code = compile(source, module_name, "exec")
        is_package = True if len(module_name.split('.')) > 1 else False # not sure, but seems accurate
        module.__file__ = filepath
        module.__loader__ = self
        if is_package:
            module.__path__ = []
            module.__package__ = module_name
        else:
            module.__package__ = module_name.split('.', 1)[0]
        exec module_code in module.__dict__
        #imp.release_lock() # it might be more correct to release the lock here instead of above.
        return module
