let SessionLoad = 1
let s:so_save = &g:so | let s:siso_save = &g:siso | setg so=0 siso=0 | setl so=-1 siso=-1
let v:this_session=expand("<sfile>:p")
silent only
silent tabonly
cd ~/programs/mpod_stuff/ORNL_MPOD_Controller
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
let s:shortmess_save = &shortmess
if &shortmess =~ 'A'
  set shortmess=aoOA
else
  set shortmess=aoO
endif
badd +26 mpodcontrol.py
badd +67 ~/programs/mpod_stuff/MatchingTest/matching2.py
badd +82 term://~/programs/mpod_stuff/ORNL_MPOD_Controller//173131:/usr/bin/zsh
badd +27 libmpodcontrol.py
badd +0 term://~/programs/mpod_stuff/ORNL_MPOD_Controller//195531:/usr/bin/zsh
argglobal
%argdel
$argadd mpodcontrol.py
edit mpodcontrol.py
let s:save_splitbelow = &splitbelow
let s:save_splitright = &splitright
set splitbelow splitright
wincmd _ | wincmd |
vsplit
wincmd _ | wincmd |
vsplit
2wincmd h
wincmd _ | wincmd |
split
1wincmd k
wincmd w
wincmd w
wincmd _ | wincmd |
split
1wincmd k
wincmd w
wincmd w
let &splitbelow = s:save_splitbelow
let &splitright = s:save_splitright
wincmd t
let s:save_winminheight = &winminheight
let s:save_winminwidth = &winminwidth
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
exe '1resize ' . ((&lines * 35 + 36) / 73)
exe 'vert 1resize ' . ((&columns * 127 + 191) / 382)
exe '2resize ' . ((&lines * 34 + 36) / 73)
exe 'vert 2resize ' . ((&columns * 127 + 191) / 382)
exe '3resize ' . ((&lines * 34 + 36) / 73)
exe 'vert 3resize ' . ((&columns * 127 + 191) / 382)
exe '4resize ' . ((&lines * 35 + 36) / 73)
exe 'vert 4resize ' . ((&columns * 127 + 191) / 382)
exe 'vert 5resize ' . ((&columns * 126 + 191) / 382)
argglobal
balt term://~/programs/mpod_stuff/ORNL_MPOD_Controller//173131:/usr/bin/zsh
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let &fdl = &fdl
let s:l = 35 - ((34 * winheight(0) + 17) / 35)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 35
normal! 043|
wincmd w
argglobal
if bufexists(fnamemodify("term://~/programs/mpod_stuff/ORNL_MPOD_Controller//173131:/usr/bin/zsh", ":p")) | buffer term://~/programs/mpod_stuff/ORNL_MPOD_Controller//173131:/usr/bin/zsh | else | edit term://~/programs/mpod_stuff/ORNL_MPOD_Controller//173131:/usr/bin/zsh | endif
if &buftype ==# 'terminal'
  silent file term://~/programs/mpod_stuff/ORNL_MPOD_Controller//173131:/usr/bin/zsh
endif
balt mpodcontrol.py
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 108 - ((33 * winheight(0) + 17) / 34)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 108
normal! 0
wincmd w
argglobal
if bufexists(fnamemodify("libmpodcontrol.py", ":p")) | buffer libmpodcontrol.py | else | edit libmpodcontrol.py | endif
if &buftype ==# 'terminal'
  silent file libmpodcontrol.py
endif
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let &fdl = &fdl
let s:l = 27 - ((26 * winheight(0) + 17) / 34)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 27
normal! 041|
wincmd w
argglobal
if bufexists(fnamemodify("term://~/programs/mpod_stuff/ORNL_MPOD_Controller//195531:/usr/bin/zsh", ":p")) | buffer term://~/programs/mpod_stuff/ORNL_MPOD_Controller//195531:/usr/bin/zsh | else | edit term://~/programs/mpod_stuff/ORNL_MPOD_Controller//195531:/usr/bin/zsh | endif
if &buftype ==# 'terminal'
  silent file term://~/programs/mpod_stuff/ORNL_MPOD_Controller//195531:/usr/bin/zsh
endif
balt libmpodcontrol.py
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 35 - ((34 * winheight(0) + 17) / 35)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 35
normal! 0
wincmd w
argglobal
if bufexists(fnamemodify("~/programs/mpod_stuff/MatchingTest/matching2.py", ":p")) | buffer ~/programs/mpod_stuff/MatchingTest/matching2.py | else | edit ~/programs/mpod_stuff/MatchingTest/matching2.py | endif
if &buftype ==# 'terminal'
  silent file ~/programs/mpod_stuff/MatchingTest/matching2.py
endif
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let &fdl = &fdl
let s:l = 70 - ((46 * winheight(0) + 35) / 70)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 70
normal! 024|
wincmd w
4wincmd w
exe '1resize ' . ((&lines * 35 + 36) / 73)
exe 'vert 1resize ' . ((&columns * 127 + 191) / 382)
exe '2resize ' . ((&lines * 34 + 36) / 73)
exe 'vert 2resize ' . ((&columns * 127 + 191) / 382)
exe '3resize ' . ((&lines * 34 + 36) / 73)
exe 'vert 3resize ' . ((&columns * 127 + 191) / 382)
exe '4resize ' . ((&lines * 35 + 36) / 73)
exe 'vert 4resize ' . ((&columns * 127 + 191) / 382)
exe 'vert 5resize ' . ((&columns * 126 + 191) / 382)
tabnext 1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0 && getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20
let &shortmess = s:shortmess_save
let &winminheight = s:save_winminheight
let &winminwidth = s:save_winminwidth
let s:sx = expand("<sfile>:p:r")."x.vim"
if filereadable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &g:so = s:so_save | let &g:siso = s:siso_save
set hlsearch
nohlsearch
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
