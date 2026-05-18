class BitwardenBackup < Formula
  include Language::Python::Virtualenv

  desc "Automated encrypted backups for Bitwarden vault"
  homepage "https://github.com/0xlxx/bitwarden-backup"
  url "https://github.com/0xlxx/bitwarden-backup/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "0000000000000000000000000000000000000000000000000000000000000000"
  license "MIT"

  depends_on "bitwarden-cli"
  depends_on "python@3.12"

  resource "click" do
    url "https://files.pythonhosted.org/packages/click/8.1.7/click-8.1.7.tar.gz"
    sha256 "ca9853ad459e787e2192211578cc907e7594e294c7ccc834310722b41b9ca6de"
  end

  resource "pyyaml" do
    url "https://files.pythonhosted.org/packages/pyyaml/6.0.1/pyyaml-6.0.1.tar.gz"
    sha256 "bfdf460b1736c775f2ba9f6a92bca30bc2095067b8a9d77876d1fad6cc3b4a43"
  end

  resource "keyring" do
    url "https://files.pythonhosted.org/packages/keyring/25.7.0/keyring-25.7.0.tar.gz"
    sha256 "1a7dfb5c5d8fe8ba4142d5dc2f1d4e46e2948bf3cca79e214848d3bbcfebedc8"
  end

  resource "cffi" do
    url "https://files.pythonhosted.org/packages/cffi/1.17.1/cffi-1.17.1.tar.gz"
    sha256 "1c39c6016c32bc48dd54561950ebd6836e1670f2ae46128f67cf49e0c504fe91"
  end

  resource "pycparser" do
    url "https://files.pythonhosted.org/packages/pycparser/2.22/pycparser-2.22.tar.gz"
    sha256 "491c8be9c040f5390f5bf44a5b07752bd07f540c5da0c70bc7dc98c7c52adb64"
  end

  resource "cryptography" do
    url "https://files.pythonhosted.org/packages/cryptography/44.0.0/cryptography-44.0.0.tar.gz"
    sha256 "5980dcb3c04a5ef0c286e84fbfc4c4444e69e77b8f9f1c8910daef5c770ff9cc"
  end

  resource "jaraco-classes" do
    url "https://files.pythonhosted.org/packages/jaraco.classes/3.4.0/jaraco.classes-3.4.0.tar.gz"
    sha256 "6f74f5b5a6e24c3f5c31824b13a3e09b3ef1e9e1ba2a7b61a06b4f48d95a508c"
  end

  resource "jaraco-context" do
    url "https://files.pythonhosted.org/packages/jaraco.context/6.0.1/jaraco.context-6.0.1.tar.gz"
    sha256 "82a0892d9ef1998b8cbd149617cc3a33e3e59e3d95d8d29479f9fb8e53e0b524"
  end

  resource "jaraco-functools" do
    url "https://files.pythonhosted.org/packages/jaraco.functools/4.5.0/jaraco.functools-4.5.0.tar.gz"
    sha256 "07e3e122bea06c42e4c49db70e1f7a5d0c55f9fca20a3b1fb3984f3ce3e88033"
  end

  resource "more-itertools" do
    url "https://files.pythonhosted.org/packages/more-itertools/11.0.2/more-itertools-11.0.2.tar.gz"
    sha256 "0e9f2e3e97286b92f189fd76e1c73fe5d56bbb4f30e4a13e83a20c3e1aac650b"
  end

  def install
    virtualenv_create(libexec, "python3.12")
    virtualenv_install_with_resources

    bin.install_symlink libexec/"bin/bw-backup"
  end

  test do
    system bin/"bw-backup", "--help"
  end
end
