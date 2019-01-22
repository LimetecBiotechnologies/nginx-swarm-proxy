import jinja2
import os
from pathlib import Path


class NginxTemplate:
    def __init__(self, template, output, prefix):
        j2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(template)), trim_blocks=True)
        self.template = j2_env.get_template(os.path.basename(template))
        self.prefix = prefix
        self.output = output

    def remove(self, container):
        conf_path = self.output + "/" + self.prefix + "_" + container['Name'] + "-" + container['ID'] + ".conf"
        if os.path.exists(conf_path):
            os.remove(conf_path)
            return True
        return False

    def remove_all(self):
        for p in Path(self.output).glob(self.prefix+"_*.conf"):
            p.unlink()

    def save(self, container):
        content = self.template.render(container)
        if not os.path.exists(self.output):
            os.makedirs(self.output)
        f = open(self.output + "/" + self.prefix + "_" + container['Name'] + "-" + container['ID'] + ".conf", "w+")
        f.write(content)
        f.close()
