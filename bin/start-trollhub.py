
if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()

    parser.add_argument('-c', '--config')
    args = parser.parse_args()
    from trollhub import create_app
    import waitress
    app = create_app(args.config)
    waitress.serve(app, listen="*:5000")
