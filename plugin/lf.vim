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
call s:init_var("file_numbered", 0)
call s:init_var("cache_path", "~/.vim/cache/vim-lf")
call s:init_var("auto_keep_open", 0)
call s:init_var("mode_normal", "NORMAL")
call s:init_var("mode_select", "SELECT")
call s:init_var("mode_keep_open", "KEEP")
call s:init_var("restore_pos", 1)

let g:vlf_mapping_main = {}
let g:vlf_mapping_cli = {}
let g:vlf_mapping_msg = {}
let g:vlf_mapping_search = {}

function! s:init_single_action(type, action, key)
  call s:init_var("action_".a:type.'_'.a:action, a:key)
  exec printf("let g:vlf_mapping_%s[a:key] = a:action", a:type)
endfunction

function! s:init_action(type, action, key) abort
  if type(a:key) == v:t_string
    call s:init_single_action(a:type, a:action, a:key)
  elseif type(a:key) == v:t_list
    for k in a:key
      call s:init_single_action(a:type, a:action, k)
    endfor
  endif
endfunction

function! s:init_action_main(action, key) abort
  call s:init_action("main", a:action, a:key)
endfunction

function! s:init_action_cli(action, key) abort
  call s:init_action("cli", a:action, a:key)
  call s:init_action("search", a:action, a:key)
endfunction

function! s:init_action_search(action, key) abort
  call s:init_action("search", a:action, a:key)
endfunction

function! s:init_action_msg(action, key) abort
  call s:init_action("msg", a:action, a:key)
endfunction

call s:init_action_main("up", "k")
call s:init_action_main("down", "j")
call s:init_action_main("top", "g")
call s:init_action_main("bottom", "G")
call s:init_action_main("scrollup", "\<c-k>")
call s:init_action_main("scrolldown", "\<c-j>")
call s:init_action_main("backward", "h")
call s:init_action_main("forward", "l")
call s:init_action_main("toggle_hidden", "s")
call s:init_action_main("edit", ["e", "\<cr>"])
call s:init_action_main("open_top", "K")
call s:init_action_main("open_bottom", "J")
call s:init_action_main("open_left", "H")
call s:init_action_main("open_right", "L")
call s:init_action_main("open_tab", "n")
call s:init_action_main("touch", "T")
call s:init_action_main("touch_edit", "t")
call s:init_action_main("delete", "d")
call s:init_action_main("delete_all", "D")
call s:init_action_main("rename", "r")
call s:init_action_main("quit", "q")
call s:init_action_main("change_keep_open", "\<space>")
call s:init_action_main("select", "v")
call s:init_action_main("select_all", "V")
call s:init_action_main("normal", "\<esc>")
call s:init_action_main("change_active", "o")
call s:init_action_main("resize", "R")
call s:init_action_main("regex_search", "/")

call s:init_action_cli("done", "\<cr>")
call s:init_action_cli("delete", ["\<bs>"])
call s:init_action_cli("left", ["\<left>", "\<c-h>"])
call s:init_action_cli("right", ["\<right>", "\<c-l>"])
call s:init_action_cli("clear", "\<c-u>")
call s:init_action_cli("go_start", "\<c-a>")
call s:init_action_cli("go_end", "\<c-e>")
call s:init_action_cli("quit", "\<esc>")

call s:init_action_msg("agree", ["y", "\<cr>"])
call s:init_action_msg("cancel", ["n", "\<esc>"])

command! -bar -nargs=1 Lf call lf#start(<q-args>)
command! -bar -nargs=0 LfLog call lf#check_log()

augroup Vimlf
  autocmd!
  autocmd VimLeave * call lf#reset_log()
  autocmd VimResized * call lf#resize()
augroup END
