from .utils import vimget, vimeval
from copy import copy


class Option(object):
    def __init__(self):
        self._popup()
        self.show_hidden = vimget("show_hidden", 0) == '1'
        self.max_file_size = vimget('max_size', 1, 1) * 1048576
        self.auto_edit = vimget('auto_edit', 0) == '1'
        self.auto_edit_cmd = vimget('auto_edit_cmd', "'edit'")
        self.laststatus = vimeval('&laststatus')
        self.t_ve = vimeval('&t_ve')

    def _popup(self):
        self.opts = {
                "maxwidth":  40,
                "minwidth":  40,
                "maxheight": 18,
                "minheight": 18,
                "pos":       "topleft",
                "line": 5,
                "mapping":   0,
                "scrollbar": 0,
                }
        self._left_opt()
        self._middle_opt()
        self._right_opt()
        #  self._info_opt()

    def _left_opt(self):
        self.left = copy(self.opts)
        self.left["col"] = 3

    def _middle_opt(self):
        self.middle = copy(self.opts)
        self.middle["col"] = 45

    def _right_opt(self):
        self.right = copy(self.opts)
        self.right["col"] = 86
        self.right["maxwidth"] = 60
        self.right["minwidth"] = 60

    #  def _info_opt(self):
        #  self.opts["line"] = 25
        #  self.opts["col"] = 3
        #  self.opts["maxwidth"] = 60
        #  self.opts["minwidth"] = 60
        #  self.opts["maxwidth"] = 60
        #  self.opts["minwidth"] = 60


lfopt = Option()
