function! s:init_var(name, default) abort
  let var = get(g:, 'vlf_'.a:name, a:default)
  exec "let g:vlf_".a:name." = var"
endfunction

call s:init_var("max_size", 1)
call s:init_var("show_hidden", 0)
call s:init_var("auto_edit", 1)
call s:init_var("auto_edit_cmd", "edit")
call s:init_var("width", 0.8)
call s:init_var("height", 0.8)
call s:init_var("panel_width", [0.25, 0.25])
call s:init_var("borderchars", ['─', '│', '─', '│', '┌', '┐', '┘', '└'])
call s:init_var("sepchar", '│')
call s:init_var("wincolor", 'Normal')
call s:init_var("inner_padding", [0, 0, 0, 0])
call s:init_var("outer_padding", [0, 1, 0, 1])
call s:init_var("border", [1, 1, 1, 1])
call s:init_var("sort_dir_first", 1)
call s:init_var("sort_ignorecase", 1)

let g:vlf_mapping_main = {}

function! s:init_single_action(action, key)
  call s:init_var("action_".a:action, a:key)
  let g:vlf_mapping_main[a:key] = a:action
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
call s:init_action("edit", ["e", "\<cr>"])
call s:init_action("open_top", "K")
call s:init_action("open_bottom", "J")
call s:init_action("open_left", "H")
call s:init_action("open_right", "L")
call s:init_action("open_tab", "n")
call s:init_action("touch", "T")
call s:init_action("touch_edit", "t")
call s:init_action("quit", "q")

let g:vlf_mapping_cli = {}

function! s:init_single_cli(action, key)
  call s:init_var("cli_".a:action, a:key)
  let g:vlf_mapping_cli[a:key] = a:action
endfunction

function! s:init_cli(action, key) abort
  if type(a:key) == v:t_string
    call s:init_single_cli(a:action, a:key)
  elseif type(a:key) == v:t_list
    for k in a:key
      call s:init_single_cli(a:action, k)
    endfor
  endif
endfunction

call s:init_cli("done", "\<cr>")
call s:init_cli("delete", ["\<bs>"])
call s:init_cli("left", ["\<left>", "\<c-h>"])
call s:init_cli("right", ["\<right>", "\<c-l>"])
call s:init_cli("clear", "\<c-u>")
call s:init_cli("go_start", "\<c-a>")
call s:init_cli("go_end", "\<c-e>")
call s:init_cli("quit", "\<esc>")

command! -bar -nargs=1 Lf call lf#start(<q-args>)
