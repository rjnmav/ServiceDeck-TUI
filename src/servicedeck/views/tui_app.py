from textual.message import Message
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, RichLog

class ServiceDeckView(App):
    """The TUI View for ServiceDeck."""
    TITLE = "ServiceDeck"
    
    CSS = """
    DataTable > .datatable--header {
        background: $secondary;
        color: $text;
        text-style: bold;
    }

    #log_view {
        border: solid $accent;
        margin: 1;
        padding: 1;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "go_back", "Back"),
        ("t", "toggle_bus", "Toggle User/System"),
        ("f", "refresh", "Refresh"),
        ("l", "view_logs", "Logs"),
        ("s", "start", "Start"),
        ("x", "stop", "Stop"),
        ("r", "restart", "Restart"),
        ("e", "enable", "Enable"),
        ("d", "disable", "Disable"),
        ("m", "mask", "Mask"),
        ("u", "unmask", "Unmask"),
    ]

    class ActionRequested(Message):
        """Sent when a unit action is requested."""
        def __init__(self, action: str, service_name: str) -> None:
            self.action = action
            self.service_name = service_name
            super().__init__()

    class ToggleBusRequested(Message):
        """Sent when switching between user/system buses."""
        pass

    class RefreshRequested(Message):
        """Sent periodically to refresh data."""
        pass

    class LogsRequested(Message):
        """Sent when service logs are requested."""
        def __init__(self, service_name: str) -> None:
            self.service_name = service_name
            super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(cursor_type="row", id="service_table")
        yield RichLog(id="log_view", highlight=True, markup=False)
        yield Footer()

    def on_mount(self) -> None:
        self.log_timer = None
        self._current_log_service = None
        self.query_one("#log_view").display = False
        table = self.query_one("#service_table")
        table.add_column("Name")
        table.add_column("Status", width=12)
        table.add_column("Sub State", width=12)
        table.add_column("Enabled", width=12)
        table.add_column("Description")
        table.focus()
        # Trigger initial data load
        self.post_message(self.RefreshRequested())

    def action_go_back(self) -> None:
        """Handle returning to the table view from logs."""
        if self.log_timer:
            self.log_timer.stop()
            self.log_timer = None
        self._current_log_service = None

        log_view = self.query_one("#log_view")
        if log_view.display:
            log_view.display = False
            table = self.query_one("#service_table")
            table.display = True
            table.focus()
            self.post_message(self.RefreshRequested())

    def action_view_logs(self) -> None:
        log_view = self.query_one("#log_view")
        if log_view.display:
            self.action_go_back()
        else:
            service = self._get_selected_service()
            if service:
                self._current_log_service = service
                self.post_message(self.LogsRequested(service))
                if self.log_timer:
                    self.log_timer.stop()
                self.log_timer = self.set_interval(2.0, self._refresh_logs)
            else:
                self.notify("No service selected", severity="warning")

    def _refresh_logs(self) -> None:
        """Timer callback to refresh current service logs."""
        if self._current_log_service:
            self.post_message(self.LogsRequested(self._current_log_service))

    def show_logs(self, logs: str, service_name: str) -> None:
        """Called by controller to display logs."""
        log_view = self.query_one("#log_view")
        log_view.clear()
        if logs:
            log_view.write(logs)
            log_view.scroll_end(animate=False)
        else:
            log_view.write("No logs found for this service.")
        self.query_one("#service_table").display = False
        log_view.display = True
        log_view.focus()
        self.sub_title = f"Logs: {service_name}"

    def action_refresh(self) -> None:
        """Manually trigger a refresh."""
        self.post_message(self.RefreshRequested())

    def on_service_deck_view_refresh_requested(self, message: RefreshRequested) -> None:
        """Handle periodic or manual refresh requests."""
        if hasattr(self, "controller"):
            self.controller.refresh_data()

    def on_service_deck_view_toggle_bus_requested(self, message: ToggleBusRequested) -> None:
        """Handle request to toggle between user and system bus."""
        if hasattr(self, "controller"):
            self.controller.toggle_bus()

    def on_service_deck_view_action_requested(self, message: ActionRequested) -> None:
        """Handle request to perform a systemd action."""
        if hasattr(self, "controller"):
            self.controller.handle_action(message.action, message.service_name)

    def on_service_deck_view_logs_requested(self, message: LogsRequested) -> None:
        """Handle request to view logs."""
        if hasattr(self, "controller"):
            self.controller.handle_logs_request(message.service_name)

    def _get_selected_service(self) -> str:
        table = self.query_one("#service_table")
        try:
            row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
            return str(row_key.value)
        except Exception:
            return None

    def action_toggle_bus(self) -> None:
        self.post_message(self.ToggleBusRequested())

    def _handle_action(self, action: str) -> None:
        service = self._get_selected_service()
        if service:
            self.post_message(self.ActionRequested(action, service))
        else:
            self.notify("No service selected", severity="warning")

    def action_start(self) -> None: self._handle_action("start")
    def action_stop(self) -> None: self._handle_action("stop")
    def action_restart(self) -> None: self._handle_action("restart")
    def action_enable(self) -> None: self._handle_action("enable")
    def action_disable(self) -> None: self._handle_action("disable")
    def action_mask(self) -> None: self._handle_action("mask")
    def action_unmask(self) -> None: self._handle_action("unmask")

    def update_table(self, services_data: list, bus_mode: str) -> None:
        """Updates the DataTable with new services data."""
        if self.query_one("#log_view").display:
            return
            
        table = self.query_one("#service_table")
        self.sub_title = f"Bus: {bus_mode} | Total: {len(services_data)}"
        
        # Save current selected row key
        current_row_key = None
        try:
            row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
            current_row_key = row_key.value
        except Exception:
            pass

        table.clear()
        for svc in services_data:
            table.add_row(
                svc["name"],
                svc["active_state"],
                svc["sub_state"],
                svc["unit_file_state"],
                svc["description"],
                key=svc["name"]
            )
        
        if current_row_key:
            try:
                table.move_cursor(row=table.get_row_index(current_row_key))
            except Exception:
                pass