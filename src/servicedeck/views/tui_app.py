from textual.message import Message
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable

class ServiceDeckView(App):
    """The TUI View for ServiceDeck."""
    TITLE = "ServiceDeck"
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("t", "toggle_bus", "Toggle User/System"),
        ("f", "refresh", "Refresh"),
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

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_column("Name")
        table.add_column("Status", width=12)
        table.add_column("Sub State", width=12)
        table.add_column("Enabled", width=12)
        table.add_column("Description")
        table.focus()
        # Trigger initial data load
        self.post_message(self.RefreshRequested())

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

    def _get_selected_service(self) -> str:
        table = self.query_one(DataTable)
        try:
            # coordinate_to_cell_key returns (RowKey, ColumnKey)
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
        table = self.query_one(DataTable)
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
        
        # Restore cursor if possible
        if current_row_key:
            try:
                table.move_cursor(row=table.get_row_index(current_row_key))
            except Exception:
                # If the service is gone, just leave it at the top or where it is
                pass
