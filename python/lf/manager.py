from pathlib import Path
from functools import partial, wraps
from .utils import vimeval, vimcmd, resetg
from .panel import DirPanel, FilePanel, InfoPanel, BorderPanel, CliPanel
from .panel import MsgRemovePanel
from .option import lfopt
from .logger import logger


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

    def check_log(self):
        vimcmd("vert botright split {}".format(self._escape_path(lfopt.log_path)))

    def reset_log(self):
        if lfopt.log_path.exists():
            lfopt.log_path.unlink()

    def start(self, cwd):
        logger.normal.info("start manager")
        self.is_quit = False
        self.is_cfile = False
        self.is_keep_open = False
        self.mode = "normal"
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

    def _escape_path(self, path):
        return str(path.resolve()).replace(' ', '\\ ')

    def _is_normal(self):
        self._set_mode()
        return self.mode == "normal"

    def _is_visual(self):
        self._set_mode()
        return self.mode == "visual"

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

    def _get_path_list(self):
        if self._is_visual():
            path_list = self.v_block.selection()
        elif self._is_normal():
            path_list = [self.curpath]
        return path_list

    def _action(self):
        while 1:
            action = vimeval("lf#action()")
            if self.is_quit:
                break

    def _set_mode(self):
        self.mode = self.middle_panel.mode

    def normal(self):
        if self.is_quit:
            return
        if self._is_visual():
            self.v_block.quit()
            self._set_mode()
        self.middle_panel._cursorline()
        self.is_keep_open = False

    def select(self):
        self.middle_panel.visual()
        self.v_block = self.middle_panel.v_block

    def change_active(self):
        if self._is_visual():
            self.v_block.change_active()

    @update_info
    def backward(self):
        if self._is_visual():
            return
        if isinstance(self.right_panel, FilePanel):
            self.right_panel.close()
            self.right_panel = DirPanel(self.curpath, 2)
        self._copy_panel(self.middle_panel, self.right_panel)
        self._copy_panel(self.left_panel, self.middle_panel)
        self.left_panel.backward()
        self._set_curpath()

    @update_info
    def forward(self):
        if self._is_visual():
            return
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
        if self._is_visual():
            self.v_block.down()
        elif self._is_normal():
            self.middle_panel.move(down=True)

    @update_all
    def up(self):
        if self._is_visual():
            self.v_block.up()
        elif self._is_normal():
            self.middle_panel.move(down=False)

    @update_all
    def top(self):
        if self._is_visual():
            self.v_block.top()
        elif self._is_normal():
            self.middle_panel.jump(top=True)

    @update_all
    def bottom(self):
        if self._is_visual():
            self.v_block.bottom()
        elif self._is_normal():
            self.middle_panel.jump(top=False)

    @update_all
    def scrollup(self):
        if self._is_visual():
            self.v_block.scroll_up()
        elif self._is_normal():
            self.middle_panel.scroll(down=False)

    @update_all
    def scrolldown(self):
        if self._is_visual():
            self.v_block.scroll_down()
        elif self._is_normal():
            self.middle_panel.scroll(down=True)

    @update_all
    def touch(self):
        if self._is_visual():
            return
        self.cli = CliPanel("FileName: ")
        self.cli.input()
        if self.cli.do:
            self.middle_panel.touch(self.cli.cmd)

    def touch_edit(self):
        if self._is_visual():
            return
        self.cli = CliPanel("FileName: ")
        self.cli.input()
        if not self.cli.do:
            return
        path = self.middle_panel.cwd.resolve() / self.cli.cmd
        if self.is_keep_open:
            self.right_panel.set_exist()
        else:
            self.is_quit = True
        self._close()
        vimcmd("edit {}".format(path))
        if self.is_keep_open:
            self._restore()
            self.is_keep_open = False
        self.normal()

    @update_all
    def delete(self):
        self.msg = MsgRemovePanel(self._get_path_list())
        self.msg.action()
        if not self.msg.do:
            return
        for path in self._get_path_list():
            print(path.exists())
            try:
                path.unlink()
            except FileNotFoundError:
                print("File not find")
        self.middle_panel.refresh(keep_pos=False)
        self.normal()

    def _open(self, cmd):
        if self.is_keep_open:
            self.right_panel.set_exist()
            self._close()
        is_open = False
        for path in self._get_path_list():
            if not path.is_file():
                continue
            is_open = True
            vimcmd("{} {}".format(cmd, self._escape_path(path)))
        if self.is_keep_open:
            self._restore()
            self.is_keep_open = False
            self.normal()
        elif is_open:
            self._close()
            self.is_quit = True
        else:
            self.normal()

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
        self.is_quit = True

    def keep_open(self):
        self.is_keep_open = True

    @update_info_path
    def toggle_hidden(self):
        self.left_panel.toggle_hidden()
        self.middle_panel.toggle_hidden()
        if self._right_is_dir():
            self.right_panel.toggle_hidden()

    def skip(self):
        pass

    @update_info_path
    def _restore(self):
        self.border_panel = BorderPanel()
        self.left_panel._create_popup()
        self.left_panel.refresh()
        self.middle_panel._create_popup()
        self.middle_panel.refresh()
        self._change_right(True)
        self.info_panel = InfoPanel(self)

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
