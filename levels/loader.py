def load_level(path):
    with open(path, "r") as file:
        return [line.strip() for line in file.readlines()]
