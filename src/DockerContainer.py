import docker


class DockerContainer:
    def __init__(self, client: docker.DockerClient, domains):
        self.client = client
        self.addresses = []
        self.domains = domains

    def find(self, port):
        containers = []
        for container in self.client.containers.list(filters={'expose': port}):
            result_container = self.convert_container(container, port)
            if result_container['Ports'].__len__() > 0:
                containers.append(self.convert_container(container, port))
        return containers

    def listen(self, event, port):
        if (event['Action'] == 'stop' and event['Type'] == 'container') or (
                event['Action'] == 'start' and event['Type'] == 'container'):
            container = self.client.containers.get(event['id'])
            result_container = self.convert_container(container, port)
            result_container['Action'] = event['Action']
            if event['Action'] == 'stop' or result_container['Ports'].__len__() > 0:
                return result_container
        return None

    def convert_container(self, container, port):
        ports = self.find_ports(container.attrs['NetworkSettings']['Ports'], port)
        return {'ID': container.attrs['Id'],
                'Name': container.attrs['Name'].replace('/', ''),
                'Labels': container.attrs['Config']['Labels'],
                'Ports': ports,
                'SourcePort': str(port),
                'Addresses': self.addresses,
                'ServerNames': self.server_names(container.attrs['Config']['Labels'],
                                                 container.attrs['Name'])}

    def server_names(self, labels, name):
        names = []
        if 'dns.name' in labels:
            names.append(labels['dns.name'])

        if 'com.docker.stack.namespace' in labels:
            start = labels['com.docker.stack.namespace'].__len__() + 1
            names += self.add_domains(name[start:] + '.' + labels['com.docker.stack.namespace'], self.domains)

        if 'com.docker.compose.service' in labels:
            names += self.add_domains(labels['com.docker.compose.service'] + '.' + labels['com.docker.compose.project'],
                                      self.domains)

        if names.__len__() == 0:
            names += self.add_domains(name, self.domains)
        return ' '.join(names)

    @staticmethod
    def find_ports(ports, port):
        tcp_port = str(port) + '/tcp'
        result_ports = []
        if port in ports:
            for res in ports[port]:
                result_ports.append(res['HostPort'])
        elif tcp_port in ports and ports[tcp_port] is not None:
            for res in ports[tcp_port]:
                result_ports.append(res['HostPort'])
        return result_ports

    @staticmethod
    def add_domains(host, domains):
        names = []
        for domain in domains:
            names.append(host + '.' + domain)
        return names
