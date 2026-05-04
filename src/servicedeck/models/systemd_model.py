from pydbus import SessionBus, SystemBus

class SystemdModel:
    def __init__(self, use_system_bus=False):
        self.use_system_bus = use_system_bus
        self._bus = None
        self._manager = None
        self._connect()

    def _connect(self):
        try:
            self._bus = SystemBus() if self.use_system_bus else SessionBus()
            # "org.freedesktop.systemd1" is the service name
            # "/org/freedesktop/systemd1" is the object path
            self._manager = self._bus.get("org.freedesktop.systemd1", "/org/freedesktop/systemd1")
        except Exception as e:
            raise

    def toggle_bus(self):
        self.use_system_bus = not self.use_system_bus
        self._connect()

    def get_services(self):
        """Fetches all loaded service units."""
        try:
            # ListUnits returns a list of structures:
            # (name, description, load_state, active_state, sub_state, followed, unit_path, job_id, job_type, job_path)
            units = self._manager.ListUnits()
            services = []
            for unit in units:
                name = unit[0]
                if name.endswith(".service"):
                    description = unit[1]
                    active_state = unit[3]
                    sub_state = unit[4]
                    
                    try:
                        # GetUnitFileState returns 'enabled', 'disabled', 'static', 'masked', etc.
                        unit_file_state = self._manager.GetUnitFileState(name)
                    except Exception:
                        unit_file_state = "unknown"
                    
                    services.append({
                        "name": name,
                        "description": description,
                        "active_state": active_state.upper(),
                        "sub_state": sub_state,
                        "unit_file_state": unit_file_state.upper()
                    })
            # Sort by name
            return sorted(services, key=lambda x: x["name"])
        except Exception as e:
            return []

    def _call_unit_method(self, method_name, unit_name, mode="replace"):
        """Generic wrapper for unit lifecycle methods (start, stop, restart)."""
        try:
            method = getattr(self._manager, method_name)
            return method(unit_name, mode)
        except Exception as e:
            raise

    def start(self, name): return self._call_unit_method("StartUnit", name)
    def stop(self, name): return self._call_unit_method("StopUnit", name)
    def restart(self, name): return self._call_unit_method("RestartUnit", name)

    def enable(self, name):
        """Enables a unit. Parameters: (names, runtime, force)"""
        try:
            return self._manager.EnableUnitFiles([name], False, True)
        except Exception as e:
            raise

    def disable(self, name):
        """Disables a unit. Parameters: (names, runtime)"""
        try:
            return self._manager.DisableUnitFiles([name], False)
        except Exception as e:
            raise

    def mask(self, name):
        """Masks a unit. Parameters: (names, runtime, force)"""
        try:
            return self._manager.MaskUnitFiles([name], False, True)
        except Exception as e:
            raise

    def unmask(self, name):
        """Unmasks a unit. Parameters: (names, runtime)"""
        try:
            return self._manager.UnmaskUnitFiles([name], False)
        except Exception as e:
            raise
