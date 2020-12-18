let g:vlf_py = "py3 "
exec g:vlf_py "<< END"
import vim, sys
from pathlib import Path
cwd = vim.eval('expand("<sfile>:p:h")')
cwd = Path(cwd) / '..' / 'python'
cwd = cwd.resolve()
sys.path.insert(0, str(cwd))
from lf.manager import *
from lf.utils import get_key
END

function! lf#start(cwd) abort
  let cwd = a:cwd == '<root>' ? '<root>' : a:cwd->fnamemodify(':p')->resolve()
  exec g:vlf_py printf("vlf_manager.start('%s')", cwd)
endfunction

function! lf#action() abort
  redraw
  let nr = getchar()
  let ch = type(nr) ? nr : nr2char(nr)
  let action = g:vlf_mapping[ch]
  exec g:vlf_py printf("vlf_manager.%s()", action)
  return action
endfunction
