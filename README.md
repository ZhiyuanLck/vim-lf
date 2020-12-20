# Preview version of vim-lf

vim-lf is a ranger-like/lf-like file explorer in vim popup.

Project is in **preview**, which means:
- Support only basic features.
- Features that already exist may be discarded.
- Default behavior may be broken.
- Current UI may be rearranged.

## Screenshot

![vim-lf][1]

## Actions

You can set the shortcut of action by
```vim
let g:vlf_action_<action> = "<key>"
```
where `<action>` is the action name and `<key>` is the shortcut.

Two styles of shortcut is supported:
1. single key such as `a, b, c, ..., A, B, ..., 1, 2, ..., -, =, ...`
2. vim special key such as `"\<c-l>", "\<esc>", "\<s-f2>"`, see all special keys by `:h key-notation`. Note that `<key>` must be leaded with `\` and be **quoted with `""`** rather than single quotes.

action          | key
------          | ---
`up`            | `"k"`
`down`          | `"j"`
`top`           | `"g"`
`bottom`        | `"G"`
`scrollup`      | `"\<c-k>"`
`scrolldown`    | `"\<c-j>"`
`backward`      | `"h"`
`forward`       | `"l"`
`toggle_hidden` | `"s"`
`edit`          | `"e"`
`open_top`      | `"K"`
`open_bottom`   | `"J"`
`open_left`     | `"H"`
`open_right`    | `"L"`
`open_tab`      | `"t"`
`quit`          | `"q"`

## Actions to be supported
- file operation
  - copy, move, paste, rename
  - undo
- filter (regex/fuzzy) (current/recursive)
  - filter directory
  - filter file
  - filter file with the same extension
- MRU directory
- zip file and tar file
- ui
  - info panel
  - devicon
- selection mode


[1]: https://github.com/ZhiyuanLck/images/blob/master/vim-lf/vim-lf.png
