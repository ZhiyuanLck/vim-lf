let s:cterm_fg = synIDattr(hlID("Normal"), "fg", "cterm") ? "fg" : 251
let s:cterm_bg = synIDattr(hlID("Normal"), "bg", "cterm") ? "bg" : 235
let s:default_highlights = {
      \ "vlf_hl_path_dir": #{
      \   ctermfg : "32",
      \   guifg : "#6699cc",
      \   cterm : "bold",
      \   gui : "bold",
      \   },
      \ "vlf_hl_path_file": #{
      \   ctermfg : "228",
      \   guifg : s:cterm_fg,
      \   },
      \ "vlf_hl_path_hidden_dir": #{
      \   ctermfg : "248",
      \   guifg : "#657371",
      \   cterm : "bold",
      \   gui : "bold",
      \   },
      \ "vlf_hl_path_hidden_file": #{
      \   ctermfg : "248",
      \   guifg : "#657371",
      \   },
      \ "vlf_hl_cursorline_0": #{
      \   ctermbg : "240",
      \   guibg : "#343d46",
      \   },
      \ "vlf_hl_cursorline_1": #{
      \   ctermbg : "23",
      \   guibg : "#343d46",
      \   },
      \ "vlf_hl_cursorline_2": #{
      \   ctermbg : "240",
      \   guibg : "#343d46",
      \   },
      \ "vlf_hl_cursorline_v": #{
      \   ctermbg : "12",
      \   },
      \ "vlf_hl_search": #{
      \   ctermfg : "46",
      \   cterm: "bold",
      \   },
      \ "vlf_hl_border": #{
      \   ctermfg : "48",
      \   guifg : "#343d46",
      \   },
      \ "vlf_hl_info_path": #{
      \   ctermfg : "255",
      \   },
      \ "vlf_hl_info_size": #{
      \   ctermfg : "223",
      \   ctermbg : "239",
      \   },
      \ "vlf_hl_info_nr": #{
      \   ctermfg : "255",
      \   ctermbg : "239",
      \   cterm: "bold",
      \   },
      \ "vlf_hl_cli_prompt": #{
      \   ctermfg : "255",
      \   cterm: "bold",
      \   },
      \ "vlf_hl_cli_cursor": #{
      \   ctermbg : "249",
      \   ctermfg : "0",
      \   },
      \ "vlf_hl_msg_warning": #{
      \   ctermfg : "9",
      \   cterm: "bold",
      \   },
      \ "vlf_hl_msg_default": #{
      \   ctermfg : "48",
      \   cterm: "bold",
      \   },
      \ "vlf_hl_msg_content": #{
      \   ctermfg : "215",
      \   },
      \ "vlf_hl_info_mode_normal": #{
      \   ctermfg : "255",
      \   ctermbg : "238",
      \   cterm: "bold",
      \   },
      \ "vlf_hl_info_mode_select": #{
      \   ctermfg : "255",
      \   ctermbg : "238",
      \   cterm: "bold",
      \   },
      \ "vlf_hl_info_mode_filter": #{
      \   ctermfg : "255",
      \   ctermbg : "238",
      \   cterm: "bold",
      \   },
      \ "vlf_hl_info_mode_keep_open": #{
      \   ctermfg : "233",
      \   ctermbg : "79",
      \   cterm: "bold",
      \   },
      \ }
let s:prop_type = #{
      \ path: ["dir", "hidden_dir", "file", "hidden_file"],
      \ info: ["size", "nr", "path", "mode_normal", "mode_select",
      \   "mode_filter", "mode_keep_open"],
      \ cli: ["prompt", "cursor"],
      \ msg: ["warning", "default", "content"],
      \ }
let s:extra_prop_patterns = #{}

function! lf#colorscheme#highlight() abort
  let hl_list = get(g:, "vlf_highlights", s:default_highlights)
  for [name, hl] in items(hl_list)
    let real_hl = get(g:, name, hl)
    let cmd = "highlight! ".name
    for [k, v] in items(real_hl)
      let cmd .= printf(" %s=%s", k, v)
    endfor
    exec cmd
  endfor
endfunction

function! s:add_proptype(prop_type, bufnr) abort
  for prop in s:prop_type[a:prop_type]
    let hl = "vlf_hl_".a:prop_type."_".prop
    call prop_type_add(prop, #{bufnr: a:bufnr, highlight: hl})
  endfor
endfunction

function! lf#colorscheme#path_prop(bufnr) abort
  call s:add_proptype("path", a:bufnr)
endfunction

function! lf#colorscheme#info_prop(bufnr) abort
  call s:add_proptype("info", a:bufnr)
endfunction

function! lf#colorscheme#cli_prop(bufnr) abort
  call s:add_proptype("cli", a:bufnr)
endfunction

function! lf#colorscheme#msg_prop(bufnr) abort
  call s:add_proptype("msg", a:bufnr)
endfunction
