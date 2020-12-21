let g:vlf_py = "py3 "
exec g:vlf_py "<< END"
import vim, sys
from pathlib import Path
cwd = vim.eval('expand("<sfile>:p:h")')
cwd = Path(cwd) / '..' / 'python'
cwd = cwd.resolve()
sys.path.insert(0, str(cwd))
from lf.manager import *
END

function! lf#start(cwd) abort
  if a:cwd == '<root>'
    let cwd = '<root>'
  elseif a:cwd == '.'
    let cwd = '.'
  else
    let cwd = a:cwd->fnamemodify(':p')
  endif
  exec g:vlf_py printf("vlf_manager.start('%s')", cwd)
endfunction

function! lf#action() abort
  redraw
  let nr = getchar()
  let ch = type(nr) ? nr : nr2char(nr)
  let action = get(g:vlf_mapping_main, ch, 'skip')
  exec g:vlf_py printf("vlf_manager.%s()", action)
  return action
endfunction

function! lf#cli() abort
  redraw
  let nr = getchar()
  let ch = type(nr) ? nr : nr2char(nr)
  let action = get(g:vlf_mapping_cli, ch, 'skip')
  exec g:vlf_py printf("vlf_manager.info_panel.%s()", action)
  return action
endfunction
