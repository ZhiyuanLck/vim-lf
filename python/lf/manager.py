from pathlib import Path
from functools import partial, wraps
from .utils import vimeval, vimcmd, resetg
from .panel import DirPanel, FilePanel, InfoPanel, BorderPanel, CliPanel
from .option import lfopt


def _update(fun, ignore):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        fun(*args, **kwargs)
        self = args[0]
        if not ignore:
            self._set_curpath()
            self._change_right()
        self.info_panel.info_path()
    return wrapper


update_all = partial(_update, ignore=False)
update_info = partial(_update, ignore=True)


def update_cursor(fun):
    def wrapper(*args, **kwargs):
        fun(*args, **kwargs)
        self = args[0]
        self._set_curpath()
        self._change_right()
    return wrapper


def update_info_path(fun):
    def wrapper(*args, **kwargs):
        fun(*args, **kwargs)
        args[0].info_panel.info_path()
    return wrapper


class Manager(object):
    def __init__(self):
        vimcmd("call lf#colorscheme#highlight()")

    def start(self, cwd):
        self.is_edit = False
        self.is_cfile = False
        self._resolve(cwd)
        vimcmd("set laststatus=0")
        vimcmd("set t_ve=")
        self._create()
        self._action()

    def _resolve(self, cwd):
        if cwd == '.':
            self.is_cfile = True
            self.cwd = Path(vimeval("expand('%:p:h')")).resolve()
            self.cfile = Path(vimeval("expand('%:p')")).resolve()
        else:
            self.cwd = Path(cwd).resolve()

    @update_info
    def _create(self):
        self.border_panel = BorderPanel()
        self._init_middle()
        self._init_left()
        self._set_curpath()
        self._change_right(True)
        self.info_panel = InfoPanel(self)

    def _init_left(self):
        self.left_panel = DirPanel(self.cwd, 0)
        self.left_panel.backward()

    def _init_middle(self):
        self.middle_panel = DirPanel(self.cwd, 1)
        self.middle_panel.refresh(keep_pos=False)
        if self.is_cfile:
            self.middle_panel._index(self.cfile)
            self.middle_panel._cursorline()

    def _action(self):
        break_list = ['edit', 'quit']
        while 1:
            action = vimeval("lf#action()")
            if self.is_edit:
                break
            if action in break_list:
                break

    @update_info
    def backward(self):
        if isinstance(self.right_panel, FilePanel):
            self.right_panel.close()
            self.right_panel = DirPanel(self.curpath, 2)
        self._copy_panel(self.middle_panel, self.right_panel)
        self._copy_panel(self.left_panel, self.middle_panel)
        self.left_panel.backward()
        self._set_curpath()

    @update_info
    def forward(self):
        if isinstance(self.right_panel, FilePanel):
            if not lfopt.auto_edit:
                self._open(lfopt.auto_edit_cmd)
        else:
            self._copy_panel(self.middle_panel, self.left_panel)
            self._copy_panel(self.right_panel, self.middle_panel)
            self._set_curpath()
            self._change_right()

    @update_all
    def down(self):
        self.middle_panel.move(down=True)

    @update_all
    def up(self):
        self.middle_panel.move(down=False)

    @update_all
    def top(self):
        self.middle_panel.jump(top=True)

    @update_all
    def bottom(self):
        self.middle_panel.jump(top=False)

    @update_all
    def scrollup(self):
        self.middle_panel.scroll(down=False)

    @update_all
    def scrolldown(self):
        self.middle_panel.scroll(down=True)

    @update_all
    def touch(self):
        self.cli = CliPanel("FileName: ")
        self.cli.input()
        self.middle_panel.touch(self.cli.cmd)

    def _open(self, cmd):
        if not self.curpath.is_file():
            return
        self._close()
        vimcmd("{} {}".format(cmd, self._cur_path()))
        self.is_edit = True
        #  resetg("wrap")
        #  resetg("buflisted")
        #  resetg("buftype")
        #  resetg("bufhidden")
        #  resetg("number")
        #  resetg("undolevels")
        #  resetg("swapfile")
        #  resetg("list")
        #  resetg("relativenumber")
        #  resetg("spell")
        #  resetg("foldenable")
        #  resetg("foldmethod")
        #  resetg("signcolumn")

    def edit(self):
        self._open("edit")

    def open_top(self):
        self._open("topleft split")

    def open_bottom(self):
        self._open("botright split")

    def open_left(self):
        self._open("vert topleft split")

    def open_right(self):
        self._open("vert botright split")

    def open_tab(self):
        self._open("tabedit")

    def quit(self):
        self._close()

    @update_info_path
    def toggle_hidden(self):
        self.left_panel.toggle_hidden()
        self.middle_panel.toggle_hidden()
        if self._right_is_dir():
            self.right_panel.toggle_hidden()

    def skip(self):
        pass

    def _right_is_dir(self):
        return isinstance(self.right_panel, DirPanel)

    def _cur_path(self):
        return str(self.curpath.resolve()).replace(' ', '\\ ')

    def _set_curpath(self):
        self.curpath = self.middle_panel.curpath()

    def _show_dir(self):
        if self.curpath is None:
            return True
        return self.curpath.is_dir()

    def _change_right(self, init=False):
        if not init:
            self.right_panel.close()
        if self._show_dir():
            self.right_panel = DirPanel(self.curpath, 2)
            if self.curpath is not None:
                self.right_panel.refresh(keep_pos=False)
        else:
            self.right_panel = FilePanel(self.curpath)

    def _close(self):
        self.border_panel.close()
        self.info_panel.close()
        self.left_panel.close()
        self.middle_panel.close()
        self.right_panel.close()
        vimcmd("set laststatus={}".format(lfopt.laststatus))
        vimcmd("set t_ve={}".format(lfopt.t_ve))

    def _copy_panel(self, a: DirPanel, b: DirPanel):
        """
        copy content of panel a to panel b
        """
        b.cwd = a.cwd
        b.index = a.index
        b.path_list = a.path_list
        b.text = a.text
        b.refresh()


vlf_manager = Manager()

__all__ = ['vlf_manager']
