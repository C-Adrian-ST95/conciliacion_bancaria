import os
import tkinter as tk

archivos_cargados = {} # Diccionario para almacenar los archivos cargados con su ruta y nombre  

def obtener_nombre_archivo(ruta):  # Obtener el nombre del archivo a partir de su ruta  
    return os.path.basename(ruta)


# Crear una clase ToolTip para mostrar mensajes emergentes en los botones u otros widgets
import tkinter as tk

class ToolTip:
    """
    Tooltip para cualquier widget de Tkinter.
    - delay_ms: retardo antes de mostrar
    - follow_mouse: si True, actualiza la posición con el movimiento
    - offset: desplazamiento (x, y) respecto al puntero
    - wraplength: ajusta el texto a ese ancho (px)
    """
    def __init__(self, widget, text, delay_ms=400, follow_mouse=True, offset=(16, 16), wraplength=320):
        self.widget = widget
        self.text = text or ""
        self.delay_ms = delay_ms
        self.follow_mouse = follow_mouse
        self.offset = offset
        self.wraplength = wraplength

        self._tipwin = None
        self._after_id = None

        # Eventos
        self.widget.bind("<Enter>", self._on_enter, add="+")
        self.widget.bind("<Leave>", self._on_leave, add="+")
        if self.follow_mouse:
            self.widget.bind("<Motion>", self._on_motion, add="+")
        # Si el widget se destruye, limpiar
        self.widget.bind("<Destroy>", self._on_destroy, add="+")

    # ------------ Eventos ------------
    def _on_enter(self, event=None):
        if not self.text.strip():
            return
        if not self._is_widget_enabled():
            return
        self._schedule_show(event)

    def _on_leave(self, event=None):
        self._cancel_scheduled()
        self._hide()

    def _on_motion(self, event):
        # Si ya está visible y seguimos el mouse, reubicar
        if self._tipwin and self.follow_mouse:
            x, y = self._pointer_xy()
            self._place_window(x, y)

    def _on_destroy(self, event=None):
        self._cancel_scheduled()
        self._hide()

    # ------------ Lógica interna ------------
    def _schedule_show(self, event=None):
        self._cancel_scheduled()
        self._after_id = self.widget.after(self.delay_ms, self._show)

    def _cancel_scheduled(self):
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None

    def _show(self):
        # No duplicar ventanas
        if self._tipwin or not self._is_widget_enabled():
            return

        self._tipwin = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # sin decoraciones
        tw.attributes("-topmost", True)

        label = tk.Label(
            tw,
            text=self.text,
            justify="left",
            background="#ffffff",
            relief="solid",
            borderwidth=1,
            font=("Arial", 8),
            padx=6, pady=4,
            wraplength=self.wraplength,
        )
        label.pack()

        # Posicionar cerca del puntero con offset; ajustar a pantalla
        x, y = self._pointer_xy()
        self._place_window(x, y)

    def _place_window(self, x, y):
        ox, oy = self.offset
        tw = self._tipwin
        if not tw:
            return

        # Posición deseada
        px = x + ox
        py = y + oy

        # Asegurar que no se salga de pantalla
        tw.update_idletasks()
        ww = tw.winfo_width()
        wh = tw.winfo_height()

        screen_w = tw.winfo_screenwidth()
        screen_h = tw.winfo_screenheight()

        if px + ww > screen_w:
            px = max(0, screen_w - ww - 2)
        if py + wh > screen_h:
            py = max(0, screen_h - wh - 2)

        tw.wm_geometry(f"+{px}+{py}")

    def _hide(self):
        if self._tipwin is not None:
            try:
                self._tipwin.destroy()
            except tk.TclError:
                pass
            self._tipwin = None

    def _pointer_xy(self):
        # Coordenadas del puntero del mouse
        try:
            return self.widget.winfo_pointerxy()
        except tk.TclError:
            # Fallback razonable
            return (self.widget.winfo_rootx(), self.widget.winfo_rooty())

    def _is_widget_enabled(self):
        # Algunos widgets no tienen 'state'; asumir enabled
        try:
            return str(self.widget["state"]) != "disabled"
        except Exception:
            return True

    # ------------ API pública ------------
    def set_text(self, text):
        """Permite actualizar el texto del tooltip en tiempo real."""
        self.text = text or ""
        if self._tipwin:
            # refrescar contenido
            for child in self._tipwin.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(text=self.text)
                    self._tipwin.update_idletasks()
                    break
