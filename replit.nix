{pkgs}: {
  deps = [
    pkgs.python311Packages.webdriver-manager
    pkgs.geckodriver
    pkgs.htop-vim
    pkgs.playwright-driver
    pkgs.gitFull
    pkgs.pango
    pkgs.glib
    pkgs.ghostscript
    pkgs.fontconfig
    pkgs.poppler_utils
    pkgs.glibcLocales
    pkgs.xcbuild
    pkgs.swig
    pkgs.openjpeg
    pkgs.mupdf
    pkgs.libjpeg_turbo
    pkgs.jbig2dec
    pkgs.harfbuzz
    pkgs.gumbo
    pkgs.freetype
    pkgs.file
    pkgs.postgresql
    pkgs.openssl
  ];
}
