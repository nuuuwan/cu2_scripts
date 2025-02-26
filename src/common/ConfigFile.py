class ConfigFile:
    def __init__(self, file_path):
        self.file_path = file_path

    def write(self, data: dict):
        content = "\n".join([f"{key} = {value}" for key, value in data.items()])
        with open(self.file_path, "w") as file:
            file.write(content)
        print(f"Wrote {len(data)} key-value pairs to {self.file_path}")
