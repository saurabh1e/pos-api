import os

from flask_migrate import Migrate, MigrateCommand
import urllib.parse as up
from flask_script import Manager
from flask import url_for

from src import api, db, ma, create_app, configs, bp, security, admin, celery, sentry

config = os.environ.get('PYTH_SRVR', 'default')

config = configs.get(config)

extensions = [api, db, ma, security, admin, celery, sentry]
bps = [bp]

app = create_app(__name__, config, extensions=extensions, blueprints=bps)

manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


@manager.shell
def _shell_context():
    return dict(
        app=app,
        db=db,
        ma=ma,
        config=config
        )


@manager.command
def list_routes():
    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)
        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = up.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)

    for line in sorted(output):
        print(line)


@manager.option('-A', '--application', dest='application', default='', required=True)
@manager.option('-n', '--name', dest='name')
@manager.option('-l', '--debug', dest='debug')
@manager.option('-P', '--pool', dest='pool')
@manager.option('-Q', '--queue', dest='queue')
@manager.option('-c', '--concurrency', dest='concurrency', default=2)
def worker(application, concurrency, pool, debug, name, queue):
    celery.start()


if __name__ == "__main__":
    manager.run()
