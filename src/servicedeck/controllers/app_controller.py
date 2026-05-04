from ..models import SystemdModel
from rich.markup import escape

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
            self.view.notify(f"Refresh failed: {escape(str(e))}", severity="error")

    def toggle_bus(self):
        """Toggles the D-Bus connection (User/System) and refreshes."""
        try:
            self.model.toggle_bus()
            self.refresh_data()
        except Exception as e:
            self.view.notify(f"Failed to switch bus: {escape(str(e))}", severity="error")

    def handle_logs_request(self, service_name: str):
        """Fetches logs from the model and updates the view."""
        try:
            logs = self.model.get_service_logs(service_name)
            self.view.show_logs(logs, service_name)
        except Exception as e:
            self.view.notify(f"Failed to fetch logs: {escape(str(e))}", severity="error")

    def handle_action(self, action: str, service_name: str):
        """Executes a unit action via the model and notifies the view."""
        try:
            method = getattr(self.model, action)
            method(service_name)
            self.view.notify(f"Successfully requested {action} for {service_name}")
            self.refresh_data()
            
            if hasattr(self.view, "set_timer"):
                self.view.set_timer(0.5, self.refresh_data)
                self.view.set_timer(1.5, self.refresh_data)
        except AttributeError:
            self.view.notify(f"Unknown action: {action}", severity="error")
        except Exception as e:
            self.view.notify(f"Failed: {escape(str(e))}", severity="error")
