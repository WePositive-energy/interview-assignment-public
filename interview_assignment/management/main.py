import typer

app = typer.Typer()


@app.callback()
def main():
    """
    Manage the microservice.
    """


if __name__ == "__main__":
    app()
