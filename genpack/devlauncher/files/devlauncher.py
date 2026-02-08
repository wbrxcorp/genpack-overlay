#!/usr/bin/env python3

import logging
import os

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gio', '2.0')
from gi.repository import Gtk, Gio, GLib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppLauncher(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='com.walbrix.devlauncher')
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        window = Gtk.ApplicationWindow(application=app)
        window.set_title(GLib.get_host_name())
        window.set_default_size(800, 600)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        flowbox = Gtk.FlowBox()
        flowbox.set_valign(Gtk.Align.START)
        flowbox.set_max_children_per_line(10)
        flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        flowbox.set_homogeneous(True)
        flowbox.set_row_spacing(10)
        flowbox.set_column_spacing(10)
        flowbox.set_margin_top(10)
        flowbox.set_margin_bottom(10)
        flowbox.set_margin_start(10)
        flowbox.set_margin_end(10)

        apps = self.load_applications()
        for app_info in apps:
            item = self.create_app_item(app_info)
            flowbox.append(item)

        scrolled.set_child(flowbox)
        window.set_child(scrolled)
        window.present()

    def load_applications(self):
        """Read all installed applications"""
        apps = Gio.DesktopAppInfo.get_all()
        visible_apps = []
        for app in apps:
            if app.should_show():
                visible_apps.append(app)
        visible_apps.sort(key=lambda a: a.get_display_name().lower())
        return visible_apps

    def create_app_item(self, app_info):
        """Create an application item"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.set_halign(Gtk.Align.CENTER)

        button = Gtk.Button()
        button.set_has_frame(False)
        button.set_size_request(80, 80)

        icon = app_info.get_icon()
        if icon:
            image = Gtk.Image.new_from_gicon(icon)
            image.set_pixel_size(48)
        else:
            image = Gtk.Image.new_from_icon_name('application-x-executable')
            image.set_pixel_size(48)

        button.set_child(image)
        button.connect('clicked', self.on_app_clicked, app_info)

        label = Gtk.Label(label=app_info.get_display_name())
        label.set_wrap(True)
        label.set_max_width_chars(12)
        label.set_ellipsize(3)  # Pango.EllipsizeMode.END
        label.set_justify(Gtk.Justification.CENTER)

        box.append(button)
        box.append(label)

        return box

    def on_app_clicked(self, button, app_info):
        """Launch the application"""
        try:
            app_info.launch(None, None)
        except GLib.Error as e:
            logger.error('Failed to launch application: %s', e.message)


def main():
    set_session_type = os.environ.get('XDG_SESSION_TYPE') != 'wayland' \
        and os.environ.get('WAYLAND_DISPLAY') is not None \
        and os.environ.get('DISPLAY') is None

    if set_session_type:
        os.environ['XDG_SESSION_TYPE'] = 'wayland'
        os.environ['MOZ_ENABLE_WAYLAND'] = '1'
        logger.info('XDG_SESSION_TYPE set to wayland')

    app = AppLauncher()
    app.run(None)

if __name__ == '__main__':
    main()
