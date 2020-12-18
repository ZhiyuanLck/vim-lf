from pathlib import Path
from .utils import vimeval, vimcmd
from .panel import DirPanel, FilePanel
from .option import lfopt


class Manager(object):
    def __init__(self):
        vimcmd("call lf#colorscheme#highlight()")

    def start(self, cwd):
        self.is_edit = False
        self.cwd = Path(cwd).resolve()
        vimcmd("set laststatus=0")
        self._create()
        self._action()

    def _create(self):
        self._set_middle()
        self._set_left()
        self.middle_panel.refresh()
        self.left_panel.backward()
        self._set_curpath()
        self._change_right(True)

    def _action(self):
        break_list = ['edit', 'quit']
        while 1:
            action = vimeval("lf#action()")
            if self.is_edit:
                break
            if action in break_list:
                break

    def backward(self):
        if isinstance(self.right_panel, FilePanel):
            self.right_panel.close()
            self.right_panel = DirPanel(self.curpath, lfopt.right, 2)
        self._copy_panel(self.middle_panel, self.right_panel)
        self._copy_panel(self.left_panel, self.middle_panel)
        self.left_panel.backward()
        self._set_curpath()

    def forward(self):
        if isinstance(self.right_panel, FilePanel):
            if not lfopt.auto_edit:
                self._open(lfopt.auto_edit_cmd)
        else:
            self._copy_panel(self.middle_panel, self.left_panel)
            self._copy_panel(self.right_panel, self.middle_panel)
            self._set_curpath()
            self._change_right()

    def down(self):
        self._move(True)

    def up(self):
        self._move(False)

    def top(self):
        self.middle_panel.jump(top=True)
        self._set_curpath()
        self._change_right()

    def bottom(self):
        self.middle_panel.jump(top=False)
        self._set_curpath()
        self._change_right()

    def scrollup(self):
        self.middle_panel.scroll(down=False)
        self._set_curpath()
        self._change_right()

    def scrolldown(self):
        self.middle_panel.scroll(down=True)
        self._set_curpath()
        self._change_right()

    def _open(self, cmd):
        if self.curpath.is_file():
            self._close()
            vimcmd("{} {}".format(cmd, self._cur_path()))
            self.is_edit = True

    def edit(self):
        self._open("edit")

    def quit(self):
        self._close()

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

    def _set_left(self):
        self.left_panel = DirPanel(self.cwd, lfopt.left, 0)

    def _set_middle(self):
        self.middle_panel = DirPanel(self.cwd, lfopt.middle, 1)

    def _move(self, down=True):
        self.curpath = self.middle_panel.down() if down else self.middle_panel.up()
        if self.curpath is not None:
            self._change_right()

    def _show_dir(self):
        if self.curpath is None:
            return True
        return self.curpath.is_dir()

    def _change_right(self, init=False):
        if not init:
            self.right_panel.close()
        if self._show_dir():
            self.right_panel = DirPanel(self.curpath, lfopt.right, 2)
            if self.curpath is not None:
                self.right_panel.refresh()
        else:
            self.right_panel = FilePanel(self.curpath, lfopt.right)

    def _close(self):
        self.left_panel.close()
        self.middle_panel.close()
        self.right_panel.close()
        vimcmd("set laststatus={}".format(lfopt.laststatus))

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
