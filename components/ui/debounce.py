# components/ui/debounce.py
class Debouncer:
    def __init__(self, widget, delay_ms=300):
        self.widget = widget
        self.delay_ms = delay_ms
        self._job = None

    def call(self, func):
        """Agenda func dentro de delay_ms, cancelando anteriores."""
        if self._job:
            self.widget.after_cancel(self._job)
        self._job = self.widget.after(self.delay_ms, func)
