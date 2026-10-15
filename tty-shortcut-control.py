#!/usr/bin/python3
"""One-switch X11 shortcut settings with per-user mapping backup."""
import os
import subprocess
import sys
from pathlib import Path

AUTOSTART = Path.home() / '.config/autostart/tty-shortcut-control.desktop'
BACKUP = Path.home() / '.config/tty-shortcut-control/original-f1.txt'


def mapping():
    result = subprocess.run(['/usr/bin/xmodmap', '-pke'], check=True,
                            capture_output=True, text=True)
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) > 3 and parts[0] == 'keycode' and parts[2] == '=':
            if 'XF86Switch_VT_1' in parts[3:] or parts[3] == 'F1':
                return line.strip()
    raise RuntimeError('Could not find the F1 key mapping.')


def apply(enabled):
    if os.environ.get('XDG_SESSION_TYPE') == 'wayland':
        raise RuntimeError('This setting requires an X11 session.')
    current = mapping()
    if enabled:
        if 'XF86Switch_VT_1' in current.split():
            return
        if not BACKUP.exists():
            raise RuntimeError('No original F1 mapping was saved. Log out and back in to restore your session defaults.')
        target = BACKUP.read_text().strip()
        if not target.startswith('keycode ') or 'XF86Switch_VT_1' not in target.split():
            raise RuntimeError('The saved F1 mapping is invalid.')
    else:
        if 'XF86Switch_VT_1' not in current.split():
            if not BACKUP.exists():
                raise RuntimeError('F1 is already remapped. Log out and back in before disabling it with this app.')
            return
        BACKUP.parent.mkdir(parents=True, exist_ok=True)
        BACKUP.write_text(current + '\n')
        target = ' '.join('F1' if value == 'XF86Switch_VT_1' else value
                          for value in current.split())
    subprocess.run(['/usr/bin/xmodmap', '-e', target],
                   check=True, capture_output=True, text=True)


def is_enabled():
    return 'XF86Switch_VT_1' in mapping().split()


def save(enabled):
    if enabled:
        AUTOSTART.unlink(missing_ok=True)
    else:
        AUTOSTART.parent.mkdir(parents=True, exist_ok=True)
        script = str(Path(__file__).resolve())
        AUTOSTART.write_text('[Desktop Entry]\nType=Application\nName=Disable Ctrl Alt F1\n'
            + 'Exec=/usr/bin/python3 "' + script + '" --disable\n'
            + 'X-GNOME-Autostart-enabled=true\nX-GNOME-Autostart-Delay=3\n')


def main():
    if '--disable' in sys.argv:
        apply(False)
        return
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk, GLib

    css = Gtk.CssProvider()
    css.load_from_data(b'''
        window { background: #f3f5f8; color: #202b3c; }
        .title { font-size: 19px; font-weight: 700; }
        .subtitle { color: #657286; font-size: 13px; }
        .card { background: #ffffff; border: 1px solid #dce2ea; border-radius: 14px; padding: 12px; }
        .key { font-family: monospace; font-size: 13px; font-weight: 600; background: #eef2f7; border: 1px solid #d2dae5; border-bottom-width: 3px; border-radius: 7px; padding: 5px 9px; }
        .plus { color: #8190a3; padding: 0 4px; }
        .setting { font-size: 13px; font-weight: 600; }
        .detail { font-size: 12px; color: #657286; }
        .status { font-size: 12px; color: #42617e; }
        switch { min-width: 52px; min-height: 28px; border-radius: 999px;
            background-image: none; background-color: #cbd3df; border: 1px solid #b8c3d2;
            color: transparent; padding: 2px; box-shadow: none; }
        switch:checked { background-image: none; background-color: #3069c5; border-color: #3069c5; color: transparent; }
        switch slider { min-width: 24px; min-height: 24px; border-radius: 999px;
            background-image: none; background-color: #ffffff; border: 0;
            box-shadow: 0 1px 3px alpha(#15243b, 0.22); margin: 0; }
        switch image { color: transparent; }
        .thai { font-size: 12px; color: #42546a; }
    ''')
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css,
                                             Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    class Window(Gtk.Window):
        def label(self, text, style):
            item = Gtk.Label(label=text, xalign=0)
            item.get_style_context().add_class(style)
            return item

        def __init__(self):
            super().__init__(title='TTY Shortcut Control')
            self.set_default_size(410, 205)
            self.set_resizable(False)
            self.set_border_width(12)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)
            self.add(box)
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
            card.set_margin_top(0)
            card.get_style_context().add_class('card')
            box.pack_start(card, True, True, 0)
            keys = Gtk.Box(spacing=4)
            for n, key in enumerate(['Ctrl', 'Alt', 'F1']):
                if n:
                    keys.pack_start(self.label('+', 'plus'), False, False, 0)
                keys.pack_start(self.label(key, 'key'), False, False, 0)
            card.pack_start(keys, False, False, 0)
            row = Gtk.Box(spacing=16)
            copy = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)
            title = self.label('Use Ctrl + Alt + F1 for switching to TTY1', 'setting')
            title.set_line_wrap(True)
            title.set_max_width_chars(29)
            copy.pack_start(title, False, False, 0)
            copy.pack_start(self.label('ใช้คีย์ลัดเพื่อเปิดหน้าคอนโซล TTY1', 'thai'), False, False, 0)
            row.pack_start(copy, True, True, 0)
            self.toggle = Gtk.Switch()
            self.toggle.set_valign(Gtk.Align.CENTER)
            self.toggle.get_accessible().set_name('ใช้ Ctrl + Alt + F1 เพื่อเปิดหน้าคอนโซล TTY1')
            row.pack_start(self.toggle, False, False, 0)
            card.pack_start(row, False, False, 0)
            self.status = self.label('', 'status')
            self.status.set_margin_top(7)
            box.pack_start(self.status, False, False, 0)
            self.toggle.set_active(is_enabled())
            self.update_status()
            self.toggle.connect('state-set', self.changed)

        def update_status(self):
            self.status.set_text(('On · เปิดใช้งาน' if self.toggle.get_active() else 'Off · ปิดใช้งาน') + ' · Saved automatically / บันทึกอัตโนมัติ' )

        def changed(self, toggle, enabled):
            old = toggle.get_active()
            previous = AUTOSTART.read_bytes() if AUTOSTART.exists() else None
            try:
                save(enabled)
                apply(enabled)
            except Exception as error:
                if previous is None:
                    AUTOSTART.unlink(missing_ok=True)
                else:
                    AUTOSTART.write_bytes(previous)
                self.status.set_text('เปลี่ยนการตั้งค่าไม่สำเร็จ: ' + str(error))
                return True
            toggle.set_state(enabled)
            toggle.set_active(enabled)
            self.update_status()
            return True

    window = Window()
    window.connect('destroy', Gtk.main_quit)
    window.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()
