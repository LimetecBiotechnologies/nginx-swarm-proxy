import docker

from src.DockerContainer import DockerContainer


class DockerService(DockerContainer):
    def __init__(self, client: docker.DockerClient, domains):
        super().__init__(client, domains)
        self.addresses = []
        self.domains = domains
        for manager in client.info()['Swarm']['RemoteManagers']:
            self.addresses.append(manager['Addr'].split(':')[0])

    def find(self, port):
        containers = []
        for container in self.client.services.list():
            if 'Ports' in container.attrs['Endpoint']:
                result_container = self.convert_container(container, port)
                if result_container['Ports'].__len__() > 0:
                    containers.append(result_container)
        return containers

    def listen(self, event, port):
        if event['Action'] == 'start' and event['Type'] == 'container':
            container = self.client.services.get(event['Actor']['Attributes']['com.docker.swarm.service.id'])
            result_container = self.convert_container(container, port)
            result_container['Action'] = event['Action']
            if result_container['Ports'].__len__() > 0:
                return result_container
        elif event['Action'] == 'stop' and event['Type'] == 'container':
            return {'Action': 'stop', 'ID': event['Actor']['Attributes']['com.docker.swarm.service.id'],
                    'Labels': event['Actor']['Attributes'],
                    'Name': event['Actor']['Attributes']['com.docker.swarm.service.name'],
                    'Ports': [],
                    'SourcePort': str(port),
                    'Addresses': self.addresses, 'ServerNames': self.server_names(event['Actor']['Attributes'],
                                                                                  event['Actor']['Attributes'][
                                                                                      'com.docker.swarm.service.name'])}
        return None

    def convert_container(self, container, port):
        ports = []
        if 'Ports' in container.attrs['Endpoint']:
            for portConfig in container.attrs['Endpoint']['Ports']:
                if portConfig['TargetPort'] == port:
                    ports.append(portConfig['PublishedPort'])
        return {'ID': container.attrs['ID'],
                'Labels': container.attrs['Spec']['Labels'],
                'Name': container.attrs['Spec']['Name'],
                'Ports': ports,
                'SourcePort': str(port),
                'Addresses': self.addresses,
                'ServerNames': self.server_names(container.attrs['Spec']['Labels'],
                                                 container.attrs['Spec']['Name'])}
