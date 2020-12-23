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

function! s:input(runner, default_action) abort
  redraw
  let nr = getchar()
  let ch = type(nr) ? nr : nr2char(nr)
  let name = a:runner == '' ? 'main' : a:runner
  exec printf("let action = get(g:vlf_mapping_%s, ch, '%s')", name, a:default_action)
  let member = a:runner == '' ? '' : a:runner.'.'
  exec g:vlf_py printf("vlf_manager.%s%s()", member, action)
  return action
endfunction

function! lf#action() abort
  call s:input('', 'skip')
endfunction

function! lf#cli() abort
  call s:input('cli', 'add')
endfunction

" function! lf#msg() abort
  
" endfunction
