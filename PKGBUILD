# Maintainer: syafa <288390380+@users.noreplay.github.com>
pkgname=wswm-ai
pkgver=1.0.0
pkgrel=1
pkgdesc="AI component for WSWM"
arch=('any')
url="https://github.com/syafareza1111/wswm.git"
license=('MIT')
depends=('python')
source=("$pkgname-$pkgver.tar.gz")
sha256sums=('SKIP')

package() {
    install -dm755 "$pkgdir/usr/share/$pkgname"
    install -dm755 "$pkgdir/usr/bin"

    # Salin seluruh file sumber dari direktori ekstrak ($srcdir)
    cp -r "$srcdir/"* "$pkgdir/usr/share/$pkgname/"

    # Buat wrapper script agar bisa dipanggil langsung via terminal
    cat << 'EOF' > "$pkgdir/usr/bin/wswm-ai"
#!/bin/bash
exec python /usr/share/wswm-ai/wswm.py "$@"
EOF
    chmod +x "$pkgdir/usr/bin/wswm-ai"
}
