from ..models import SystemdModel

class AppController:
    """The Controller that manages logic between SystemdModel and ServiceDeckView."""
    
    def __init__(self, view):
        self.view = view
        self.model = SystemdModel()
        
    def refresh_data(self):
        """Fetches latest service data from the model and pushes to the view."""
        try:
            services = self.model.get_services()
            bus_mode = "System" if self.model.use_system_bus else "User"
            self.view.update_table(services, bus_mode)
        except Exception as e:
            self.view.notify(f"Refresh failed: {e}", severity="error")

    def toggle_bus(self):
        """Toggles the D-Bus connection (User/System) and refreshes."""
        try:
            self.model.toggle_bus()
            self.refresh_data()
        except Exception as e:
            self.view.notify(f"Failed to switch bus: {e}", severity="error")

    def handle_action(self, action: str, service_name: str):
        """Executes a unit action via the model and notifies the view."""
        try:
            # Map action string to model method
            method = getattr(self.model, action)
            method(service_name)
            self.view.notify(f"Successfully requested {action} for {service_name}")
            # Immediate refresh to show the new state
            self.refresh_data()
            
            # Since systemd operations (start/stop/restart) are often asynchronous jobs,
            # we schedule follow-up refreshes to capture the final state.
            if hasattr(self.view, "set_timer"):
                self.view.set_timer(0.5, self.refresh_data)
                self.view.set_timer(1.5, self.refresh_data)
        except AttributeError:
            self.view.notify(f"Unknown action: {action}", severity="error")
        except Exception as e:
            self.view.notify(f"Failed: {e}", severity="error")
