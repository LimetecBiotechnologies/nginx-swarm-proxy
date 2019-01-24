import docker
from .DockerContainer import DockerContainer
from .NginxTemplate import NginxTemplate


class Main:
    def __init__(self, port, domains, template, output):
        self.client = docker.from_env()
        self.port = port
        self.domains = domains
        self.template = NginxTemplate(template, output)

        if 'ID' not in self.client.swarm.attrs:
            print("WARNING: not running on swarm manager! can only proxy local containers!")
            self.docker = DockerContainer(self.client, self.port, self.domains)
        else:
            print("ERROR: swarm mode currently not supported!... coming soon")
            exit(-1)

    def resynchronize(self):
        containers = self.docker.find()
        self.template.remove_all()

        print('register the following containers:')
        for container in containers:
            print(container['ClientPort'] + '=>' + container['ServerPort'] + '=>' + container[
                'ContainerPort'] + " = " + ' '.join(container['ServerNames']) + ' (' + container['ID'] + ')')
            self.template.save(container)

    def handle(self):
        for event in self.client.events(decode=True):
            container = self.docker.handle(event)
            if container is not None:
                if container['Action'] == 'stop':
                    print('unregister: ' + ' '.join(container['ServerNames']) + ' (' + container['ID'] + ')')
                    self.template.remove(container)
                elif container['Action'] == 'start':
                    print('register: ' + container['ClientPort'] + '=>' + container['ServerPort'] + '=>' + container[
                        'ContainerPort'] + " = " + ' '.join(container['ServerNames']) + ' (' + container['ID'] + ')')
                    self.template.save(container)
