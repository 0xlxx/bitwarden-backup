class BitwardenBackup < Formula
  include Language::Python::Virtualenv

  desc "Automated daily encrypted backups for Bitwarden vault"
  homepage "https://github.com/0xlxx/bitwarden-backup"
  url "https://github.com/0xlxx/bitwarden-backup/archive/refs/tags/v0.1.6.tar.gz"
  sha256 "b35c23a1419296e447cfe236ee21e94b22ba8a34699bb2b437bb6ed0afad559b"
  license "MIT"

  depends_on "bitwarden-cli"
  depends_on "python@3.12"

  def install
    venv = libexec
    system Formula["python@3.12"].opt_bin/"python3.12", "-m", "venv", "--upgrade-deps", venv
    system venv/"bin/pip", "install", buildpath
    bin.install_symlink venv/"bin/bw-backup"
  end

  test do
    system bin/"bw-backup", "--help"
  end
end
