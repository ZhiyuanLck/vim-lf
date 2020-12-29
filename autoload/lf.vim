let g:vlf_py = "py3 "
exec g:vlf_py "<< END"
import vim, sys
from pathlib import Path
cwd = vim.eval('expand("<sfile>:p:h")')
cwd = Path(cwd) / '..' / 'python'
cwd = cwd.resolve()
sys.path.insert(0, str(cwd))
from lf.manager import *
import logging
logger = logging.getLogger()
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

let s:name_dict = {
      \ '': 'main',
      \ 'cli_panel': 'cli',
      \ 'msg_panel': 'msg',
      \ 'search_panel': 'search',
      \ }

function! s:action(runner, default_action) abort
  redraw
  let nr = getchar()
  let ch = type(nr) ? nr : nr2char(nr)
  let name = s:name_dict[a:runner]
  exec printf("let action = get(g:vlf_mapping_%s, ch, '%s')", name, a:default_action)
  let member = a:runner == '' ? '' : a:runner.'.'
  if a:runner == ''
    exec g:vlf_py printf("logger.info('<{}_mode_action: %s>'.format(vlf_manager.mode))", action)
  else
    exec g:vlf_py printf("logger.info('<%s_action: %s>')", name, action)
  endif
  exec g:vlf_py printf("vlf_manager.%s%s()", member, action)
  return action
endfunction

function! lf#action() abort
  return s:action('', 'skip')
endfunction

function! lf#cli() abort
  return s:action('cli_panel', 'add')
endfunction

function! lf#search() abort
  return s:action('search_panel', 'add')
endfunction

function! lf#msg() abort
  return s:action('msg_panel', 'skip')
endfunction

function! lf#check_log() abort
  exec g:vlf_py "vlf_manager.check_log()"
endfunction

function! lf#resize() abort
  exec g:vlf_py "vlf_manager.resize()"
endfunction

function! lf#restore_pos() abort
  if line("'\"") > 0 && line("'\"") <= line("$") && g:vlf_restore_pos == 1
    exec "norm! g`\""
  endif
endfunction

function! lf#clear_log() abort
  exec g:vlf_py "vlf_manager.clear_log()"
endfunction

function! lf#leave() abort
  exec g:vlf_py "logger.info('running code before leaving vim')"
  exec g:vlf_py "vlf_manager.reset_log()"
  exec g:vlf_py "vlf_manager.dump()"
  exec g:vlf_py "logger.info('LEAVE')"
endfunction
