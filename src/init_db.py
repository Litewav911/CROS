from database import Base, engine
import models


def main():
    Base.metadata.create_all(engine)

    print("CROS database tables created successfully.")


if __name__ == "__main__":
    main()