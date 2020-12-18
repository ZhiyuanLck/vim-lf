function! s:init_var(name, default) abort
  let var = get(g:, 'vlf_'.a:name, a:default)
  exec "let g:vlf_".a:name." = var"
endfunction
call s:init_var("max_size", 1)
call s:init_var("show_hidden", 0)
command! -bar -nargs=1 Lf call lf#start(<q-args>)
