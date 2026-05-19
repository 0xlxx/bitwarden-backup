class BitwardenBackup < Formula
  include Language::Python::Virtualenv

  desc "Automated daily encrypted backups for Bitwarden vault"
  homepage "https://github.com/0xlxx/bitwarden-backup"
  url "https://github.com/0xlxx/bitwarden-backup/archive/refs/tags/v0.1.1.tar.gz"
  sha256 "28935560850b2754ea7714a079097bb91a0206879de38ee7b9281f2be64ae65a"
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
