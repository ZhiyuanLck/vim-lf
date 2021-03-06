import logging
import shutil
import pickle
import vim
from collections import deque
from pathlib import Path
from functools import partial, wraps
from .utils import vimeval, vimcmd, resetg
from .panel import *
from .option import lfopt, PopupOption


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
        vimcmd("echo ''")
    return wrapper


update_all = partial(_update, ignore=False)
update_info = partial(_update, ignore=True)


class Manager(object):
    def __init__(self):
        self._is_start = False
        logger.info("INIT manager")
        vimcmd("call lf#colorscheme#highlight()")
        if lfopt.regex_search_history.exists():
            with open(lfopt.regex_search_history, 'rb') as f:
                self.regex_search_history = pickle.load(f)
                logger.info("load regex search history")
        else:
            self.regex_search_history = deque(maxlen=lfopt.max_regex_search_history)
            logger.info("no regex search history, init as []")

    def save_regex(self, pattern):
        self.regex_search_history.appendleft(pattern)

    def dump(self):
        try:
            with open(lfopt.regex_search_history, 'wb') as f:
                pickle.dump(self.regex_search_history, f)
                logger.info("dump {} regex search history".format(len(self.regex_search_history)))
        except Exception as e:
            logger.error(e)

    def check_log(self):
        vimcmd("vert botright split {}".format(self._escape_path(lfopt.log_path)))
        vimcmd("norm! G")

    def clear_log(self):
        if lfopt.log_path.exists():
            lfopt.log_path.unlink()

    def reset_log(self):
        for path in lfopt.log_dir.glob("*.log"):
            if path != lfopt.log_path:
                path.unlink()
                logger.info("delete log before today")

    def start(self, cwd):
        self._is_start = True
        logger.info("START manager")
        self.is_quit = False
        self.is_cfile = False
        self.is_keep_open = False
        self.filter_select = False
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
        path_str = str(path.resolve()).replace('\\', '\\\\').replace(' ', '\\ ')
        logger.info("final path string is {}".format(path_str))
        return path_str

    def _is_normal(self):
        #  if not self._is_filter():
            #  self._set_mode()
        return self.mode == "normal"

    def _is_select(self):
        #  if not self._is_filter():
            #  self._set_mode()
        return self.mode == "select"

    def _is_filter(self):
        return self.mode == "filter"

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
        if not self._is_start:
            return
        panels = ["border", "left", "middle", "right", "info", "cli", "msg", "search"]
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
        logger.info("try to get selected path_list")
        if is_all:
            logger.info("get all paths in panel")
            return self.middle_panel.get_path_list()
        if self._is_select():
            path_list = self.v_block.selection()
        else:
            path_list = [self._curpath()]
        logger.info("get path_list of length {}".format(len(path_list)))
        return path_list

    def _action(self):
        while 1:
            try:
                action = vimeval("lf#action()")
            except vim.error as e:
                logger.error("unexpected vim errors: {}".format(e))
                vimsg("Error", "ignored unexpected vim error: {}".format(e))
                continue
            if self.is_quit:
                break

    def _set_mode(self):
        self.mode = self.middle_panel.mode

    @update_info
    def normal(self):
        if self.is_quit: # if quit manager, no need to change mode
            return
        if self._is_select():
            logger.info("quit select mode")
            self.v_block.quit()
        elif self._is_filter():
            logger.info("quit filter mode")
            try:
                self.search_panel.restore()
            except AttributeError:
                self.middle_panel.refresh(item=self._curpath())
            self._change_right()
            self.mode = "normal"
        if self._is_select():
            if self.filter_select:
                logger.info("back to filter mode")
                self.mode = "filter"
            else:
                self.mode = "normal"
        self.middle_panel._cursorline()
        self.filter_select = False
        if lfopt.auto_keep_open:
            self.is_keep_open = False

    @update_info
    def select(self):
        if self.empty():
            logger.info("empty directory, action cancels")
            return
        if self._is_filter():
            self.filter_select = True
            logger.info("remember filter mode")
        self.mode = "select"
        self.middle_panel.select()
        self.v_block = self.middle_panel.v_block

    def select_all(self):
        if self.empty():
            logger.info("empty directory, action cancels")
            return
        self.select()
        self.v_block.select_all()

    def change_active(self):
        if self._is_select():
            self.v_block.change_active()

    @update_info
    def backward(self):
        if self._is_select():
            return
        if self._is_filter():
            self.normal()
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
        else:
            self.middle_panel.move(down=True)

    @update_all
    def up(self):
        if self._is_select():
            self.v_block.up()
        else:
            self.middle_panel.move(down=False)

    @update_all
    def top(self):
        if self._is_select():
            self.v_block.top()
        else:
            self.middle_panel.jump(top=True)

    @update_all
    def bottom(self):
        if self._is_select():
            self.v_block.bottom()
        else:
            self.middle_panel.jump(top=False)

    @update_all
    def scrollup(self):
        if self._is_select():
            self.v_block.scroll_up()
        else:
            self.middle_panel.scroll(down=False)

    @update_all
    def scrolldown(self):
        if self._is_select():
            self.v_block.scroll_down()
        else:
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

    def _restore_pos(self):
        vimcmd("call lf#restore_pos()")

    @update_info
    def manual_update_info(self):
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
            self._save_middle()
        else:
            self.quit()
        vimcmd("edit {}".format(self._escape_path(path)))
        if self.is_keep_open:
            self._restore()
            self.is_keep_open = False
        self.normal()

    def _save_middle(self):
        self.right_panel.set_exist()
        self._close()
        self._middle_backup = [self.middle_panel.index, self.middle_panel.text]

    def _open(self, cmd):
        logger.info("START opening with command `{}`".format(cmd))
        if self.is_keep_open:
            self._save_middle()
        is_open = False # whether the file is opened
        for path in self._get_path_list():
            if not path.is_file():
                logger.warning("ignore directory {}".format(path))
                continue
            logger.info("open file {}".format(path))
            try:
                vimcmd("{} {}".format(cmd, self._escape_path(path)))
                is_open = True
                self._restore_pos()
            except vim.error as e:
                logger.error(e)
        if self.is_keep_open: # keep_open, restore the panel
            self._restore()
            if lfopt.auto_keep_open:
                self.is_keep_open = False
            self.normal()
        # file is opened with no error, make sure file buffer is not wiped out! And then quit
        elif is_open:
            if isinstance(self.right_panel, FilePanel):
                self.right_panel.set_exist()
            self.quit()
        else: # file open failed, back to normal mode
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

    def regex_search(self):
        if self._is_select():
            self.normal()
        self.search_panel = RegexSearchPanel(self)
        self.search_panel.input()

    def regex_search_all(self):
        self.middle_panel.glob_all()
        self.regex_search()

    def _filter(self, mode):
        if self._is_select():
            self.normal()
        self.mode = "filter"
        getattr(self.middle_panel, "filter_{}".format(mode))()

    @update_info
    def filter_dir(self):
        self._filter("dir")

    @update_info
    def filter_file(self):
        self._filter("file")

    @update_info
    def filter_ext(self):
        self._filter("ext")

    def quit(self):
        self._is_start = False
        self._close()
        self.is_quit = True
        vimcmd("set laststatus={}".format(lfopt.laststatus))
        vimcmd("set t_ve={}".format(lfopt.t_ve))
        logger.info("QUIT manager")

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
        self.middle_panel.restore(self._middle_backup)
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
