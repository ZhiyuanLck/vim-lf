from .utils import vimget, vimeval
from copy import copy


class Popup(object):
    def __init__(self, width, height, col, line, padding, zindex=10, border=False):
        self.opt = {
                "pos":       "topleft",
                "border":    [0, 0, 0, 0],
                "borderhighlight": ["vlf_hl_border"],
                "padding":   padding,
                "mapping":   0,
                "scrollbar": 0,
                }
        if border:
            self.set_border()
        self._parse_size(width, height)
        #  self.set_width(width)
        #  self.set_height(height)
        self.set_zindex(zindex)
        self.set_anchor(col, line)

    def _parse_size(self, width, height):
        pad = self.opt["padding"]
        bor = self.opt["border"]
        self.win_width = width
        self.win_height = height
        self.inner_width = width - bor[1] - bor[3]
        self.inner_height = height - bor[0] - bor[2]
        minus_width = pad[1] + pad[3] + bor[1] + bor[3]
        minus_height = pad[0] + pad[2] + bor[0] + bor[2]
        self.offset_col = pad[3] + bor[3]
        self.offset_line = pad[0] + bor[0]
        width -= minus_width
        self.opt["maxwidth"] = width
        self.opt["minwidth"] = width
        self.width = width
        height -= minus_height
        self.opt["maxheight"] = height
        self.opt["minheight"] = height
        self.height = height

    def shifted_anchor(self):
        return self.col + self.offset_col, self.line + self.offset_line

    def set_anchor(self, col, line):
        self.opt["col"] = col
        self.opt["line"] = line
        self.col = col
        self.line = line

    def set_zindex(self, zindex):
        self.opt["zindex"] = zindex

    def set_border(self):
        border = vimget('border', [1, 1, 1, 1])
        border = [int(x) for x in border]
        borderchars = vimget('borderchars', ['─', '│', '─', '│', '┌', '┐', '┘', '└'])
        self.opt["border"] = border
        self.opt["borderchars"] = borderchars
        self.opt["borderhighlight"] = ["vlf_hl_border"]


class Option(object):
    def __init__(self):
        self._variables()
        self._popup()

    def _variables(self):
        self.laststatus = vimeval('&laststatus')
        self.t_ve = vimeval('&t_ve')
        self.lines = vimeval('&lines', 1)
        self.columns = vimeval('&columns', 1)
        self.show_hidden = vimget("show_hidden", 0) == '1'
        self.max_file_size = vimget('max_size', 1, 1) * 1048576
        self.auto_edit = vimget('auto_edit', 0) == '1'
        self.auto_edit_cmd = vimget('auto_edit_cmd', "'edit'")

    def _popup(self):
        self.width = vimget('width', 0.8, 2)
        self.height = vimget('height', 0.8, 2)
        panel_width = vimget('panel_width', [0.25, 0.25])
        self.panel_width = [float(x) for x in panel_width]
        self.wincolor = vimget('wincolor', "'Normal'")
        self.sepchar = vimget('sepchar', "'│'")
        inner_padding = vimget('inner_padding', [0, 0, 0, 0])
        self.inner_padding = [int(x) for x in inner_padding]
        outer_padding = vimget('outer_padding', [0, 0, 0, 0])
        self.outer_padding = [int(x) for x in outer_padding]
        border = vimget('border', [1, 1, 1, 1])
        self.border = [int(x) for x in border]
        self.min_width = 80
        self.min_height = 10
        self.min_dir_width = 20
        self.min_file_width = 40
        self._border_opt()
        self._left_opt()
        self._middle_opt()
        self._right_opt()
        self._info_opt()
        self._sep_opt()

    def popup(self, name):
        return getattr(self, "popup_{}".format(name)).opt

    def _real_val(self, min_val, val, max_val, total):
        max_val = min(max_val, total)
        if val < 0:
            return min_val
        if val > max_val:
            return max_val
        if val > 1:
            return max(int(val), min_val)
        return max(int(val * total), min_val)

    def _real(self, min_val, val, total):
        return self._real_val(min_val, val, total, total)

    def _border_opt(self):
        width = self._real(self.min_width, self.width, self.columns)
        height = self._real(self.min_height, self.height, self.lines)
        self.popup_border = Popup(width = width, height = height,
                col = (self.columns - width) // 2 + 1,
                line = (self.lines - height) // 2 + 1,
                padding = self.outer_padding, zindex = 1, border = True,
                )
        self.inner_width = self.popup_border.width
        self.inner_height = self.popup_border.height - 1

    def _left_opt(self):
        width = self._real(self.min_dir_width, self.panel_width[0], self.inner_width)
        self.popup_left = Popup(width, self.inner_height,
                *self.popup_border.shifted_anchor(),
                padding = self.inner_padding
                )

    def _middle_opt(self):
        width = self._real(self.min_dir_width, self.panel_width[1], self.inner_width)
        self.popup_middle = Popup(width = width,
                height = self.inner_height,
                col = self.popup_left.col + self.popup_left.win_width + 1, # + sep
                line = self.popup_left.line,
                padding = self.inner_padding
                )

    def _right_opt(self):
        width = self.inner_width - self.popup_left.win_width - self.popup_middle.win_width - 2 # - sep
        self.popup_right = Popup(width = width,
                height = self.inner_height,
                col = self.popup_middle.col + self.popup_middle.win_width + 1, # + sep
                line = self.popup_left.line,
                padding = self.inner_padding
                )

    def _info_opt(self):
        self.popup_info = Popup(width = self.popup_border.inner_width,
                height = 1,
                col = self.popup_border.col + 1,
                line = self.popup_left.line + self.popup_left.win_height,
                padding = [0, 0, 0, 0]
                )

    def _sep_opt(self):
        self.popup_sep_a = Popup(width=1, height=self.inner_height,
                col = self.popup_middle.col - 1,
                line = self.popup_left.line,
                padding = [0, 0, 0, 0]
                )
        self.popup_sep_b = Popup(width=1, height=self.inner_height,
                col = self.popup_right.col - 1,
                line = self.popup_left.line,
                padding = [0, 0, 0, 0]
                )


lfopt = Option()
