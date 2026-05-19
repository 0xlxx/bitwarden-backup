class BitwardenBackup < Formula
  include Language::Python::Virtualenv

  desc "Automated daily encrypted backups for Bitwarden vault"
  homepage "https://github.com/0xlxx/bitwarden-backup"
  url "https://github.com/0xlxx/bitwarden-backup/archive/refs/tags/v0.1.4.tar.gz"
  sha256 "272367cff3fe9d8ff145c45ff075f110ef3b3f04dd1fa87e1ca24fb99ea7f789"
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
