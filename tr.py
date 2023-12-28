import os

print(os.path.abspath('db_folder'))
b = os.path.dirname(__file__)
print(os.path.join(os.path.dirname(__file__), 'database', 'image_log.db'))

print(f"sqlite:///{os.path.join(os.path.dirname(__file__), 'db', 'captured_images.db')}")
