# Preview version of vim-lf

vim-lf is a ranger-like/lf-like file explorer in vim popup. Call it simply by `:Lf <path>`, for example:
```vim
:Lf . " open current directory
:Lf ~ " open home directory
```

Project is in **preview**, which means:
- Support only basic features.
- Features that already exist may be discarded.
- Default behavior may be broken.
- Current UI may be rearranged.
- Support for nvim is not considered in short term.

## Screenshot

![vim-lf][1]

## Main action

You can set the shortcut of main action by
```vim
let g:vlf_action_<action> = "<key>"
```
where `<action>` is the action name and `<key>` is the shortcut.

Two styles of shortcut is supported:
1. single key such as `a, b, c, ..., A, B, ..., 1, 2, ..., -, =, ...`
2. vim special key such as `"\<c-l>", "\<esc>", "\<s-f2>"`, see all special keys by `:h key-notation`. Note that `<key>` must be leaded with `\` and be **quoted with `""`** rather than single quotes.

action             | key
------             | ---
`up`               | `"k"`
`down`             | `"j"`
`top`              | `"g"`
`bottom`           | `"G"`
`scrollup`         | `"\<c-k>"`
`scrolldown`       | `"\<c-j>"`
`backward`         | `"h"`
`forward`          | `"l"`
`toggle_hidden`    | `"s"`
`edit`             | `["e", "\<cr>"]`
`touch_edit`       | `"t"`
`touch`            | `"T"`
`open_top`         | `"K"`
`open_bottom`      | `"J"`
`open_left`        | `"H"`
`open_right`       | `"L"`
`open_tab`         | `"n"`
`quit`             | `"q"`
`change_keep_open` | `"\<space>"`
`select`           | `"v"`
`select_all`       | `"V"`
`normal`           | `"\<esc>"`
`change_active`    | `"o"`
`resize`           | `"R"`
`regex_search`     | `"/"`

## Cli action

You can set the shortcut of main action by
```vim
let g:vlf_cli_<action> = "<key>"
```

action     | key
------     | ---
`done`     | `"\<cr>"`
`delete`   | `"\<bs>"`
`left`     | `"["\<left>", "\<c-h>"]"`
`right`    | `"["\<right>", "\<c-l>"]"`
`clear`    | `"\<c-u>"`
`go_start` | `"\<c-a>"`
`go_end`   | `"\<c-e>"`
`quit`     | `"\<quit>"`

## Search action

When you are in `search` mode, all cli actions are supported and there are some extra actions.

action            | key
------            | ---
`previous_search` | `["\<c-k>", "\<up>"]`
`next_search`     | `["\<c-j>", "\<down>"]`

## Features to be supported
- file operation
  - copy, move, paste
  - undo
- filter (fuzzy) (current/recursive)
  - filter directory
  - filter file
  - filter file with the same extension
- search completion
- MRU directory/file
- Open manager through file under cursor
- zip file and tar file
- ui
  - separator
  - devicon


[1]: https://github.com/ZhiyuanLck/images/blob/master/vim-lf/vim-lf.png
