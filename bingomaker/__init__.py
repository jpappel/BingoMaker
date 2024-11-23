from app import create_app

__all__ = ["create_app"]

if __name__ == "__main__":
    create_app().run(port=8080, debug=True)
