import jinja2
import os
from pathlib import Path


class NginxTemplate:
    def __init__(self, template, output):
        j2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(template)), trim_blocks=True)
        self.template = j2_env.get_template(os.path.basename(template))
        self.output = output

    def remove(self, container):
        conf_path = self.output + "/" + container['ID'] + ".conf"
        if os.path.exists(conf_path):
            os.remove(conf_path)
            return True
        return False

    def remove_all(self):
        for p in Path(self.output).glob("*.conf"):
            p.unlink()

    def save(self, container):
        container['ServerNames'] = ' '.join(container['ServerNames'])
        content = self.template.render({'container': container})
        if not os.path.exists(self.output):
            os.makedirs(self.output)
        f = open(self.output + "/" + container['ID'] + ".conf", "w+")
        f.write(content)
        f.close()
