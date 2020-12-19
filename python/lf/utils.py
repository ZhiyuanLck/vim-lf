import vim

from functools import partial
from pathlib import Path

vimcmd = vim.command


def vimeval(cmd, to_int=0):
    """
    :to_int:
        0 for original
        1 for int
        2 for float
    """
    r = vim.eval(cmd)
    if to_int == 0:
        return r
    if to_int == 1:
        return int(r)
    return float(r)


def _vimget(namespace, prefix, var, default, eval_mode=0):
    return vimeval("get({}, '{}_{}', {})".format(namespace, prefix, var, default), eval_mode)


vimget = partial(_vimget, 'g:', 'vlf')


def setlocal(winid, cmd):
    vimcmd("call win_execute({}, 'setlocal {}')".format(winid, cmd))


def winexec(winid, cmd):
    vimcmd("call win_execute({}, '{}')".format(winid, cmd))


def get_cwd():
    cwd = vimeval("fnamemodify(resolve(expand('%:p')), ':p:h')")
    use_root = vimget("use_root", 1) == '1'
    if not use_root:
        return cwd
    is_root = False
    root_marker = vimget("root_marker", ['.root', '.git', '.svn', '.hg', '.project'])
    level = vimget("root_search_level", 5, 1)
    cur = Path(cwd)
    n = 1
    while n <= level and cur != cur.parent:
        if n > 1:
            cur = cur.parent
        for marker in root_marker:
            f = cur / marker
            if not f.is_symlink() and f.exists():
                is_root = True
                break
        if is_root:
            break
        n += 1
    return str(cur) if is_root and cur != Path.home() else cwd


def vimsg(type, msg):
    vimcmd(r"""echohl {} | echom "{}" | echohl None""".format(type, msg))
