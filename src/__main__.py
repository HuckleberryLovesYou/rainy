import app
import cli

def main():
    args = cli.parse_cli_args()
    app.main(args)



if __name__ == "__main__":
    main()