from __future__ import print_function
import clr

from pyrevit import EXEC_PARAMS
from pyrevit.coreutils.logger import get_logger
from pyrevit.coreutils import rvtprotocol
from pyrevit.coreutils import prepare_html_str

clr.AddReferenceByPartialName('System.Windows.Forms')
clr.AddReferenceByPartialName('System.Drawing')

# noinspection PyUnresolvedReferences
import System.Drawing
# noinspection PyUnresolvedReferences
import System.Windows


logger = get_logger(__name__)


class PyRevitConsoleWindow:
    """Wrapper to interact with the output console window."""

    def __init__(self, window_handle):
        """Sets up the wrapper from the input dot net window handler"""
        self.__winhandle__ = window_handle
        self.__winhandle__.UrlHandler = self._handle_protocol_url

    @staticmethod
    def _handle_protocol_url(url):
        """
        This is a function assgined to the __winhandle__.UrlHandler which
         is a delegate. Everytime WebBrowser is asked to handle a link with
         a protocol other than http, it'll call this function.
        System.Windows.Forms.WebBrowser returns a string with misc stuff
         before the actual link, when it can't recognize the protocol.
        This function cleans up the link for the pyRevit protocol handler.

        Args:
            url (str): the url coming from Forms.WebBrowser
        """
        try:
            if rvtprotocol.PROTOCOL_NAME in url:
                cleaned_url = url.split(rvtprotocol.PROTOCOL_NAME)[1]
                # get rid of the slash at the end
                if cleaned_url.endswith('/'):
                    cleaned_url = cleaned_url.replace('/', '')

                # process cleaned data
                rvtprotocol.process_url(cleaned_url)
        except Exception as exec_err:
            logger.error('Error handling link | {}'.format(exec_err))

    def set_title(self, new_title):
        self.__winhandle__.Text = new_title

    def set_width(self, width):
        self.__winhandle__.Width = width

    def set_height(self, height):
        self.__winhandle__.Height = height

    def set_font(self, font_family_name, font_size):
        # noinspection PyUnresolvedReferences
        self.__winhandle__.txtStdOut.Font = System.Drawing.Font(font_family_name, font_size,
                                                                System.Drawing.FontStyle.Regular,
                                                                System.Drawing.GraphicsUnit.Point)

    def resize(self, width, height):
        self.set_width(width)
        self.set_height(height)

    def get_title(self):
        return self.__winhandle__.Text

    def get_width(self):
        return self.__winhandle__.Width

    def get_height(self):
        return self.__winhandle__.Height

    def close(self):
        self.__winhandle__.Close()

    def hide(self):
        self.__winhandle__.Hide()

    def show(self):
        self.__winhandle__.Show()

    def save_contents(self, dest_file):
        html = self.__winhandle__.txtStdOut.Document.Body.OuterHtml.encode('ascii', 'ignore')
        doc_txt = self.__winhandle__.txtStdOut.DocumentText
        full_html = doc_txt.lower().replace('<body></body>', html)
        with open(dest_file, 'w') as output_file:
            output_file.write(full_html)

    def open_url(self, dest_url):
        self.__winhandle__.txtStdOut.Navigate(dest_url, False)

    def update_progress(self, cur_value, max_value):
        self.__winhandle__.UpdateProgressBar(cur_value, max_value)

    @staticmethod
    def print_html(html_str):
        print(prepare_html_str(html_str), end="")

    @staticmethod
    def print_code(code_str):
        nbsp = '&nbsp;'
        code_div = '<div style="font-family:courier new;' \
                   'border-style: solid;' \
                   'border-width:0 0 0 5;' \
                   'border-color:#87b012;' \
                   'background:#ececec;' \
                   'color:#3e3d3d;' \
                   'line-height: 150%;' \
                   'padding:10;' \
                   'margin:10 0 10 0">' \
                   '{}' \
                   '</div>'

        print(prepare_html_str(code_div.format(code_str.replace('    ', nbsp*4))), end="")

    @staticmethod
    def print_md(md_str):
        from pyrevit.coreutils.console import markdown
        print(prepare_html_str(markdown.markdown(md_str)), end="")

    @staticmethod
    def linkify(*args):
        return prepare_html_str(rvtprotocol.make_url(args))

# creates an instance of PyRevitConsoleWindow with the recovered __window__ handler.
output_window = PyRevitConsoleWindow(EXEC_PARAMS.window_handle)

# This snippet is for backup only:
# __window__ used to be added to local scope by pyRevitLoader.dll, thus it needed to be extracted from caller scope
# pyRevitLoader.dll has been modified to add __window__ to globals.
# from .coreutils import inspect_calling_scope_local_var
# win_handler = pyrevit.coreutils.inspect_calling_scope_local_var('__window__')
# if win_handler:
#     output_window = PyRevitConsoleWindow(win_handler)
