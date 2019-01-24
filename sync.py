import argparse
from src.Main import Main

parser = argparse.ArgumentParser(
    description='listen on the docker socket and synchronize the vhost redirection with nginx')
parser.add_argument("port")
parser.add_argument("--template", default='default.conf.tpl', help='the template for config generation')
parser.add_argument("--domains", default='localhost',
                    help='a list of top level domains used for all containers proxied by this application')
parser.add_argument("--output", default='/etc/nginx/conf.d/', help='output directory for the generated config files')

args = parser.parse_args()

main = Main(args.port, args.domains.split(','), args.template, args.output)
main.resynchronize()
main.handle()
