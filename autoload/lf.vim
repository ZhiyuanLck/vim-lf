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
  let cwd = a:cwd == '<root>' ? '<root>' : a:cwd->fnamemodify(':p')->resolve()
  exec g:vlf_py printf("lf_manager.start('%s')", cwd)
endfunction

function! lf#action(winid, key) abort
  if a:key == "\<esc>"
    call popup_close(a:winid)
  else
    exec g:vlf_py "lf_manager.set()"
  endif
endfunction

let s:filetype = 'autocmd filetypedetect'->execute()->split("\n")

function! lf#filetype(ext) abort
  if a:ext == ''
    return ''
  endif
  let filetype = copy(s:filetype)
  let matching = filetype->filter('v:val =~ "\*".a:ext." "')->sort()->uniq()
  echom matching
  if len(matching) == 1 && matching[0]  =~ 'setf'
     return matchstr(matching[0], 'setf\s\+\zs\k\+')
  endif
  return ''
endfunction
