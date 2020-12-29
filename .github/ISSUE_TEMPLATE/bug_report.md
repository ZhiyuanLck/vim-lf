---
name: Bug report
about: Create a report to help us improve
title: ''
labels: ''
assignees: ''

---

* Make sure to search for a solution in old issues before posting a new one.
* Learn at least a minimum of Markdown formatting (https://guides.github.com/features/mastering-markdown).

** Basic Information**
- platform and distribution (windows 10, ubuntu 18.04, ...)
- terminal (gnome terminal, xterm, alacritty, ...)
- vim version (for example: vim 8.2 included patch 2017 or the output of `vim --version`)

**Describe the bug**
- a clear and concise description of what the bug is. Maybe need some screenshots.
- error message (output of `:messages`)
- useful information in the output of `:LfLog` such as
  - lines that contain `ERROR
  - lines between `INIT manager` and `QUIT` (log of one run of the manager)
  - lines between `INIT` and `LEAVE` (log during the vim is running)

**To Reproduce**
You may need a minimal setting file: `minimal.vim`
```vim
set nocompatible
" change to your own path
let &runtimepath  = '~/.vim/bundles/vim-lf,' . &runtimepath
```
Then run vim via `vim --clean -S minimal.vim somefile`.
Steps to reproduce the behavior in vim:
1. In normal mode, press ...
2. run ex commands ...
3. ...

**Additional context**
Add any other context about the problem here.
