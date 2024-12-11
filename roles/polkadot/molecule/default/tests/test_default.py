def test_polkadot_binary(host):
    binary = host.file("/usr/local/bin/polkadot")
    assert binary.exists
    assert binary.is_file
    assert binary.mode == 0o755

def test_polkadot_service(host):
    service = host.service("polkadot")
    assert service.is_enabled

def test_polkadot_user(host):
    user = host.user("polkadot")
    assert user.exists
    assert user.shell == "/sbin/nologin"
    assert user.system

def test_polkadot_directories(host):
    dirs = [
        "/data/polkadot",
        "/var/run/polkadot",
        "/var/log/polkadot"
    ]
    for dir_path in dirs:
        dir = host.file(dir_path)
        assert dir.exists
        assert dir.is_directory
        assert dir.user == "polkadot"
        assert dir.group == "polkadot"

def test_polkadot_ports(host):
    ports = [30333, 9933, 9944, 9615]
    for port in ports:
        socket = host.socket(f"tcp://0.0.0.0:{port}")
        assert socket.is_listening
