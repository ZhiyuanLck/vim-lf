let s:cterm_fg = synIDattr(hlID("Normal"), "fg", "cterm") ? "fg" : 251
let s:cterm_bg = synIDattr(hlID("Normal"), "bg", "cterm") ? "bg" : 235
let s:default_highlights = {
      \ "vlf_hl_dir": #{
      \   ctermfg : "68",
      \   guifg : "#6699cc",
      \   cterm : "bold",
      \   gui : "bold",
      \   },
      \ "vlf_hl_file": #{
      \   ctermfg : s:cterm_fg,
      \   guifg : s:cterm_fg,
      \   },
      \ "vlf_hl_hidden_dir": #{
      \   ctermfg : "243",
      \   guifg : "#657371",
      \   cterm : "bold",
      \   gui : "bold",
      \   },
      \ "vlf_hl_hidden_file": #{
      \   ctermfg : "243",
      \   guifg : "#657371",
      \   },
      \ "vlf_hl_cursorline_0": #{
      \   ctermbg : "222",
      \   guibg : "#343d46",
      \   },
      \ "vlf_hl_cursorline_1": #{
      \   ctermbg : "222",
      \   guibg : "#343d46",
      \   },
      \ "vlf_hl_cursorline_2": #{
      \   ctermbg : "222",
      \   guibg : "#343d46",
      \   },
      \ }
let s:base_prop = ["dir", "hidden_dir", "file", "hidden_file"]
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

function! lf#colorscheme#prop(bufnr) abort
  for prop in s:base_prop
    let hl = "vlf_hl_".prop
    call prop_type_add(prop, #{bufnr: a:bufnr, highlight: hl})
  endfor
  call prop_type_add("cursorline", #{bufnr: a:bufnr, highlight: hl})
endfunction
