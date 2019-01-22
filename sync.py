import sys
import docker
import requests
from src.DockerContainer import DockerContainer
from src.DockerService import DockerService
from src.NginxTemplate import NginxTemplate
import subprocess


class Main:
    def __init__(self, port, template, domains, output):
        self.client = docker.from_env()
        self.port = port
        self.template = NginxTemplate(template, output, str(port))
        if 'ID' not in self.client.swarm.attrs:
            print("WARNING: not running on swarm manager! can only proxy local containers!")
            self.dockerInterface = DockerContainer(self.client, domains)
        else:
            self.dockerInterface = DockerService(self.client, domains)

    def initialize(self):
        containers = self.dockerInterface.find(self.port)
        self.template.remove_all()
        for container in containers:
            self.template.save(container)

    def listen(self, port):
        for event in self.client.events(decode=True):
            container = self.dockerInterface.listen(event, port)
            if container is not None:
                reload_nginx = False
                if container['Action'] == 'start':
                    print('register new container on port ' + str(port) + ' with the following dns names: ' + container[
                        'ServerNames'])
                    self.template.save(container)
                    reload_nginx = True
                elif container['Action'] == 'stop':
                    if self.template.remove(container):
                        print(
                            'container on port ' + str(port) + ' with the following dns names unregistered: ' +
                            container['ServerNames'])
                        reload_nginx = True

                if reload_nginx is True:
                    subprocess.call('nginx -s reload', shell=True)


try:
    main = Main(int(sys.argv[1]), sys.argv[2], [sys.argv[3]], sys.argv[4])
    main.initialize()
    main.listen(int(sys.argv[1]))
except requests.exceptions.ConnectionError:
    print("can't connect to docker daemon!")
