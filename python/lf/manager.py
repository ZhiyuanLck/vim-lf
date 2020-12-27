import logging
import shutil
from pathlib import Path
from functools import partial, wraps
from .utils import vimeval, vimcmd, resetg
from .panel import DirPanel, FilePanel, InfoPanel, BorderPanel, CliPanel
from .panel import MsgRemovePanel
from .option import lfopt, Option


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(lfopt.log_path)
formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(message)s (%(filename)s:%(lineno)s)',
        '%Y-%m-%d %H:%M:%S'
        )
handler.setFormatter(formatter)
logger.addHandler(handler)


def _update(fun, ignore):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        fun(*args, **kwargs)
        self = args[0]
        if not ignore:
            self._change_right()
        self.info_panel.info_path()
    return wrapper


update_all = partial(_update, ignore=False)
update_info = partial(_update, ignore=True)


class Manager(object):
    def __init__(self):
        vimcmd("call lf#colorscheme#highlight()")

    def check_log(self):
        vimcmd("vert botright split {}".format(self._escape_path(lfopt.log_path)))

    def reset_log(self):
        if lfopt.log_path.exists():
            lfopt.log_path.unlink()

    def start(self, cwd):
        logger.info("start manager")
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
        logger.info("init cwd as {}".format(self.cwd))

    def _escape_path(self, path):
        path_str = str(path.resolve()).replace(' ', '\\ ')
        logger.info("final path string is {}".format(path_str))
        return path_str

    def _is_normal(self):
        self._set_mode()
        return self.mode == "normal"

    def _is_select(self):
        self._set_mode()
        return self.mode == "select"

    @update_info
    def _create(self):
        logger.info("init UI")
        self.border_panel = BorderPanel()
        self._init_middle()
        self._init_left()
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
        logger.info("initialize cursor pos as {}".format(self.middle_panel.index))

    def resize(self):
        panels = ["border", "left", "middle", "right", "info", "cli", "msg"]
        for panel in panels:
            try:
                getattr(self, panel + "_panel").resize(panel)
            except:
                pass
        self.left_panel.refresh()
        self.middle_panel.refresh()

    def empty(self):
        return self.middle_panel.empty()

    def _get_path_list(self, is_all=False):
        if is_all:
            return self.middle_panel.get_path_list()
        if self._is_select():
            path_list = self.v_block.selection()
        elif self._is_normal():
            path_list = [self._curpath()]
        return path_list

    def _action(self):
        while 1:
            action = vimeval("lf#action()")
            if self.is_quit:
                break

    def _set_mode(self):
        self.mode = self.middle_panel.mode

    @update_info
    def normal(self):
        logger.info("current mode is {}, now try to back to normal mode".format(self.mode))
        if self.is_quit:
            return
        if self._is_select():
            self.v_block.quit()
            self._set_mode()
        self.middle_panel._cursorline()
        if lfopt.auto_keep_open:
            self.is_keep_open = False

    @update_info
    def select(self):
        if self.empty():
            return
        self.middle_panel.select()
        self.v_block = self.middle_panel.v_block

    def select_all(self):
        self.select()

    def change_active(self):
        if self._is_select():
            self.v_block.change_active()

    @update_info
    def backward(self):
        if self._is_select():
            return
        if isinstance(self.right_panel, FilePanel):
            self.right_panel.close()
            self.right_panel = DirPanel(self._curpath(), 2)
        self._copy_panel(self.middle_panel, self.right_panel)
        self._copy_panel(self.left_panel, self.middle_panel)
        self.left_panel.backward()
        logger.info("change cwd to {}".format(self._curpath()))

    @update_info
    def forward(self):
        if self._is_select():
            return
        if isinstance(self.right_panel, FilePanel):
            if not lfopt.auto_edit:
                self._open(lfopt.auto_edit_cmd)
        else:
            self._copy_panel(self.middle_panel, self.left_panel)
            self._copy_panel(self.right_panel, self.middle_panel)
            self._change_right()
        logger.info("change cwd to {}".format(self._curpath()))

    @update_all
    def down(self):
        if self._is_select():
            self.v_block.down()
        elif self._is_normal():
            self.middle_panel.move(down=True)

    @update_all
    def up(self):
        if self._is_select():
            self.v_block.up()
        elif self._is_normal():
            self.middle_panel.move(down=False)

    @update_all
    def top(self):
        if self._is_select():
            self.v_block.top()
        elif self._is_normal():
            self.middle_panel.jump(top=True)

    @update_all
    def bottom(self):
        if self._is_select():
            self.v_block.bottom()
        elif self._is_normal():
            self.middle_panel.jump(top=False)

    @update_all
    def scrollup(self):
        if self._is_select():
            self.v_block.scroll_up()
        elif self._is_normal():
            self.middle_panel.scroll(down=False)

    @update_all
    def scrolldown(self):
        if self._is_select():
            self.v_block.scroll_down()
        elif self._is_normal():
            self.middle_panel.scroll(down=True)

    @update_all
    def delete(self):
        self._delete(is_all=False)

    @update_all
    def delete_all(self):
        self._delete(is_all=True)

    def _delete(self, is_all):
        if self.empty():
            return
        path = self._get_path_list(is_all)
        if path == []:  # do nothing
            return
        logger.info("START deletion")
        self.msg_panel = MsgRemovePanel(self._get_path_list(is_all))
        self.msg_panel.action()
        if not self.msg_panel.do:
            logger.info("action cancels")
            return
        for path in self._get_path_list(is_all):
            file_or_dir = 'file' if path.is_file() else 'directory'
            logger.info("delete {} {}".format(file_or_dir, path))
            try:
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)
                logger.info("deletion success")
            except FileNotFoundError:
                logger.error("deletion failed")
                print("File not find")
        self.middle_panel.refresh(keep_pos=False)
        self.normal()
        logger.info("END deletion")

    @update_all
    def rename(self):
        if self.empty() or self._is_select():
            return
        self.cli_panel = CliPanel("Newname: ")
        self.cli_panel.input()
        if not self.cli_panel.do:
            logger.info("action cancels")
            return
        target = self.middle_panel.cwd / self.cli_panel.cmd
        self._curpath().rename(target)
        self.middle_panel.refresh(item=target)

    def copy(self):
        pass

    @update_all
    def touch(self):
        if self._is_select():
            return
        self.cli_panel = CliPanel("FileName: ")
        self.cli_panel.input()
        if self.cli_panel.do:
            self.middle_panel.touch(self.cli_panel.cmd)
        else:
            logger.info("action cancels")

    def touch_edit(self):
        if self._is_select():
            return
        self.cli_panel = CliPanel("FileName: ")
        self.cli_panel.input()
        if not self.cli_panel.do:
            logger.info("action cancels")
            return
        path = self.middle_panel.cwd.resolve(True) / self.cli_panel.cmd
        logger.info("edit file {}".format(path))
        if self.is_keep_open:
            self.right_panel.set_exist()
            self._close()
        else:
            self.quit()
        vimcmd("edit {}".format(self._escape_path(path)))
        if self.is_keep_open:
            self._restore()
            self.is_keep_open = False
        self.normal()

    def _open(self, cmd):
        logger.info("START opening with command `{}`".format(cmd))
        if self.is_keep_open:
            self.right_panel.set_exist()
            self._close()
        is_open = False
        for path in self._get_path_list():
            if not path.is_file():
                logger.warning("ignore directory {}".format(path))
                continue
            logger.info("open file {}".format(path))
            is_open = True
            vimcmd("{} {}".format(cmd, self._escape_path(path)))
        if self.is_keep_open:
            self._restore()
            if lfopt.auto_keep_open:
                self.is_keep_open = False
            self.normal()
        elif is_open:
            if isinstance(self.right_panel, FilePanel):
                self.right_panel.set_exist()
            self.quit()
        else:
            self.normal()
        logger.info("END opening")

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
        vimcmd("set laststatus={}".format(lfopt.laststatus))
        vimcmd("set t_ve={}".format(lfopt.t_ve))

    @update_info
    def change_keep_open(self):
        self.is_keep_open = not self.is_keep_open

    @update_info
    def toggle_hidden(self):
        self.left_panel.toggle_hidden()
        self.middle_panel.toggle_hidden()
        if self._right_is_dir():
            self.right_panel.toggle_hidden()

    def skip(self):
        pass

    @update_info
    def _restore(self):
        logger.info("restore UI")
        self.border_panel = BorderPanel()
        self.left_panel._create_popup()
        self.left_panel.refresh()
        self.middle_panel._create_popup()
        self.middle_panel.refresh()
        self._change_right(True)
        self.info_panel = InfoPanel(self)

    def _right_is_dir(self):
        return isinstance(self.right_panel, DirPanel)

    def _curpath(self):
        return self.middle_panel.curpath()

    def _show_dir(self):
        if self._curpath() is None:
            return True
        return self._curpath().is_dir()

    def _change_right(self, init=False):
        if not init:
            self.right_panel.close()
        if self._show_dir():
            self.right_panel = DirPanel(self._curpath(), 2)
            if self._curpath() is not None:
                self.right_panel.refresh(keep_pos=False)
        else:
            self.right_panel = FilePanel(self._curpath())

    def _close(self):
        logger.info("close panels")
        self.border_panel.close()
        self.info_panel.close()
        self.left_panel.close()
        self.middle_panel.close()
        self.right_panel.close()

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
