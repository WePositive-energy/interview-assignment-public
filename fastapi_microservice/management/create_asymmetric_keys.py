import subprocess

from typer import Typer

app = Typer()


@app.command()
def generate_keys():
    proc = subprocess.run(["openssl", "genrsa", "4096"], stdout=subprocess.PIPE)
    # lines=proc.stdout.readlines()
    lines = proc.stdout.decode("utf-8").split("\n")
    private_key = (
        "".join(lines)
        .replace("-----BEGIN PRIVATE KEY-----", "")
        .replace("-----END PRIVATE KEY-----", "")
    )
    proc2 = subprocess.Popen(
        ["openssl", "rsa", "-pubout", "-outform", "PEM"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
    )
    stdout, _ = proc2.communicate(
        input=f"-----BEGIN PRIVATE KEY-----\n{private_key}\n-----END PRIVATE KEY-----\n".encode()
    )
    lines = stdout.decode("utf-8").split("\n")
    public_key = (
        "".join(lines)
        .replace("-----BEGIN PUBLIC KEY-----", "")
        .replace("-----END PUBLIC KEY-----", "")
    )
    print(f"public key:\n{public_key}")  # noqa: T201
    print(f"private key:\n{private_key}")  # noqa: T201
