#!/usr/bin/python
import sys
import gtk
import gobject


def parse_invenio_log():
    """Returns a dictionary ordered by dates"""
    res = {}

    cur_exception = None
    cur_data = None

    f = open("/opt/invenio/var/log/invenio.err", "r")
    for line in f.readlines():
        if line[:2] == "* ":
            cur_exception = {"stackframe_details" : [], "traceback_details" : [], "user_details": [], "header": []}
            date = line[2:12]
            if not (date in res):
                res[date] = []

            res[date].append(cur_exception)
            cur_data = "header"

        if line[:7] == "** User":
            cur_data = "user_details"
        elif line[:12] == "** Traceback":
            cur_data = "traceback_details"
        elif line[:8] == "** Stack":
            cur_data = "stackframe_details"
        else:
            cur_exception[cur_data].append(line)
    for date in res:
        res[date].reverse()
    return res

class TutorialTextEditor:
    def on_log_reader_window_destroy(self, widget, data=None):
        print "Quiting"
        gtk.main_quit()

    def __init__(self):

        builder = gtk.Builder()
        builder.add_from_file("logreader.glade")

        self.window = builder.get_object("log_reader_window")
        self.exceptions_store = gtk.TreeStore(gobject.TYPE_STRING)
        self.exceptions_list = builder.get_object("exceptions_list")
        self.exceptions_list.set_model(self.exceptions_store)


        builder.connect_signals(self)
        self.window.connect("destroy", lambda w: gtk.main_quit())

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Exception", renderer, text=0)
        self.exceptions_list.append_column(column)
        self.datelinks = []
        self.exceptions = None
        self.exception_message_view = builder.get_object("exception_message_view")
        self.user_details_view = builder.get_object("user_details_view")
        self.traceback_detail_view = builder.get_object("traceback_detail_view")
        self.frame_details_view = builder.get_object("frame_details_view")


    def reload_button_clicked(self, evt):
        self.update_exceptions()

    def update_exceptions(self):
        self.exceptions = parse_invenio_log()
        editor.exceptions_store.clear()
        self.datelinks = []
        for date in self.exceptions:
            self.datelinks.append(date)
            tmp_root = self.exceptions_store.append(None, (date, ))
            for ex in self.exceptions[date]:
                self.exceptions_store.append(tmp_root, (" ".join(ex["header"]), ))

    def on_exceptions_list_row_activated(self, tv, pos, col):
        if len(pos) < 2:
            return

        ex = self.exceptions[self.datelinks[pos[0]]][pos[1]]

        self.exception_message_view.get_buffer().set_text("\n".join(ex["header"]))
        self.user_details_view.get_buffer().set_text("\n".join(ex["user_details"]))
        self.traceback_detail_view.get_buffer().set_text("\n".join(ex["traceback_details"]))
        self.frame_details_view.get_buffer().set_text("\n".join(ex["stackframe_details"]))

if __name__ == "__main__":
    editor = TutorialTextEditor()
    editor.window.show()
    editor.update_exceptions()

    gtk.main()
