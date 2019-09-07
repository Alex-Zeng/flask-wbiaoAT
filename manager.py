from flask_script import Manager, Server
from main import app
from flask_migrate import Migrate, MigrateCommand
from ext import db

# Init manager object via main object
manager = Manager(app)
migrate = Migrate(app, db)
# Create a new commands: server
# This command will be run the Flask development_env server
manager.add_command("server", Server())
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()