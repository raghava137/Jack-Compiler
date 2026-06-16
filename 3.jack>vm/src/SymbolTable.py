class SymbolTable:
    def __init__(self):
        self._class_scope = {}
        self._sub_scope = {}
        self._counters = {
            'static': 0,
            'field': 0,
            'argument': 0,
            'local': 0
        }

    def reset_sub(self):
        self._sub_scope = {}
        self._counters['argument'] = 0
        self._counters['local'] = 0

    def define(self, name, typ, kind):
        n = self._counters[kind]
        self._counters[kind] += 1
        entry = (typ, kind, n)
        if kind in ('static', 'field'):
            self._class_scope[name] = entry
        else:
            self._sub_scope[name] = entry

    def kind_of(self, name):
        if name in self._sub_scope:
            return self._sub_scope[name][1]
        if name in self._class_scope:
            return self._class_scope[name][1]
        return None

    def type_of(self, name):
        if name in self._sub_scope:
            return self._sub_scope[name][0]
        if name in self._class_scope:
            return self._class_scope[name][0]
        return None

    def index_of(self, name):
        if name in self._sub_scope:
            return self._sub_scope[name][2]
        if name in self._class_scope:
            return self._class_scope[name][2]
        return None

    def var_count(self, kind):
        return self._counters[kind]
