function! s:init_var(name, default) abort
  let var = get(g:, 'vlf_'.a:name, a:default)
  exec "let g:vlf_".a:name." = var"
endfunction
call s:init_var("max_size", 1)
call s:init_var("show_hidden", 0)
call s:init_var("auto_edit", 1)
call s:init_var("auto_edit_cmd", "edit")

let g:vlf_mapping = {}

function! s:init_single_action(action, key)
  call s:init_var("action_".a:action, a:key)
  let g:vlf_mapping[a:key] = a:action
endfunction

function! s:init_action(action, key) abort
  if type(a:key) == v:t_string
    call s:init_single_action(a:action, a:key)
  elseif type(a:key) == v:t_list
    for k in a:key
      call s:init_single_action(a:action, k)
    endfor
  endif
endfunction

call s:init_action("up", "k")
call s:init_action("down", "j")
call s:init_action("top", "g")
call s:init_action("bottom", "G")
call s:init_action("scrollup", "\<c-k>")
call s:init_action("scrolldown", "\<c-j>")
call s:init_action("backward", "h")
call s:init_action("forward", "l")
call s:init_action("toggle_hidden", "s")
call s:init_action("edit", "e")
call s:init_action("quit", "q")

command! -bar -nargs=1 Lf call lf#start(<q-args>)
