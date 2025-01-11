mkdir -p ~/.local/bin
mkdir -p ~/.local/share/pandoc/filters
mkdir -p ~/.local/share/fonts

sudo apt-get install -y librsvg2-bin

wget https://github.com/jgm/pandoc/releases/download/3.4/pandoc-3.4-1-amd64.deb
sudo dpkg -i pandoc-3.4-1-amd64.deb

wget https://github.com/lierdakil/pandoc-crossref/releases/download/v0.3.18.0/pandoc-crossref-Linux.tar.xz
tar -xf pandoc-crossref-Linux.tar.xz -C ~/.local/bin

wget -O ~/.local/share/pandoc/filters/include-files.lua https://github.com/pandoc-ext/include-files/raw/refs/heads/main/include-files.lua

wget -qO- "https://yihui.org/tinytex/install-bin-unix.sh" | sh
tlmgr install ctex setspace subfig caption textpos
# tlmgr install svg transparent ifplatform catchfile

# Get Source Han Sans Fonts
wget -O ~/.local/share/fonts/SourceHanSansCN-Regular.otf https://github.com/adobe-fonts/source-han-sans/raw/refs/heads/release/SubsetOTF/CN/SourceHanSansCN-Regular.otf
wget -O ~/.local/share/fonts/SourceHanSansCN-Medium.otf https://github.com/adobe-fonts/source-han-sans/raw/refs/heads/release/SubsetOTF/CN/SourceHanSansCN-Medium.otf
wget -O ~/.local/share/fonts/SourceHanSansCN-Bold.otf https://github.com/adobe-fonts/source-han-sans/raw/refs/heads/release/SubsetOTF/CN/SourceHanSansCN-Bold.otf
