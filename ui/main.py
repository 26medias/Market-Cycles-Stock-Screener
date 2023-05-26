from application import Application
import sys

def main():
    app = Application(sys.argv)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
