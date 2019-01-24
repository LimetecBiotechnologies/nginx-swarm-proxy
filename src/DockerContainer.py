import docker

NGINX_CLIENT_PORT_LABEL = 'nginx.proxy.client.port'
NGINX_CONTAINER_PORT_LABEL = 'nginx.proxy.container.port'
NGINX_HOST_LABEL='nginx.proxy.host'


class DockerContainer:
    def __init__(self, client: docker.DockerClient, port, domains):
        self.client = client
        self.port = port
        self.domains = domains

    # find all containers required for this proxy-port
    def find(self):
        containers = []
        for container in self.client.containers.list(filters={'label': NGINX_CLIENT_PORT_LABEL + '=' + str(self.port)}):
            containers.append(self.convert_container(container))
        return containers

    # return event-container if required for proxy-port
    def handle(self, event):
        if (event['Action'] == 'stop' and event['Type'] == 'container') or (
                event['Action'] == 'start' and event['Type'] == 'container'):
            container = self.client.containers.get(event['id'])
            if NGINX_CLIENT_PORT_LABEL in container.attrs['Config']['Labels'] and container.attrs['Config']['Labels'][
                NGINX_CLIENT_PORT_LABEL] == str(self.port):
                result_container = self.convert_container(container)
                result_container['Action'] = event['Action']
                return result_container
        return None

    def convert_container(self, container):
        container_port = self.port
        if 'nginx.proxy.container.port' in container.attrs['Config']['Labels']:
            container_port = container.attrs['Config']['Labels'][NGINX_CONTAINER_PORT_LABEL]

        return {
            'ID': container.attrs['Id']
            , 'ContainerPort': container_port
            , 'ServerPort': self.find_port(container.attrs['NetworkSettings']['Ports'], container_port)
            , 'ClientPort': self.port
            , 'ServerNames': self.find_server_names(container)
        }

    def find_server_names(self, container):
        names = []
        if NGINX_HOST_LABEL in container.attrs['Config']['Labels']:
            names.append(container.attrs['Config']['Labels'][NGINX_HOST_LABEL])
        elif 'com.docker.compose.project' in container.attrs['Config']['Labels']:
            names.append(container.attrs['Config']['Labels']['com.docker.compose.service'] + '.' +
                         container.attrs['Config']['Labels']['com.docker.compose.project'])
        # todo: com.docker.stack
        else:
            names.append(container.attrs['Name'].replace('/', ''))

        server_names = []
        for name in names:
            for domain in self.domains:
                server_names.append(name + '.' + domain)
        return server_names

    @staticmethod
    def find_port(ports, port):
        tcp_port = str(port) + '/tcp'
        if tcp_port in ports and ports[tcp_port] is not None:
            return ports[tcp_port][0]['HostPort']
        return None
