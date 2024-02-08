from flask_script import Manager, Server
from flask_migrate import MigrateCommand, Migrate
from src.dms.app import create_app, db

app = create_app()
manager = Manager(app)

migrate = Migrate(app, db)
manager.add_command("runserver", Server())
manager.add_command("db", MigrateCommand)

if __name__ == '__main__':
    manager.run()
