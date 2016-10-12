# utils.py
import configparser
import sys
import os
import requests

from client import Setup


config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), 'tss.conf'))
# print(config.sections())

default = config['DEFAULT']
user = config['USER']

default_apiserver = default.get('ApiServer', 'localhost')
default_port = default.get('Port', 8000)
user_product = user.get('Product', 'rhos')


def get_choices(product, product_meta):
    '''
    if Setup.port_scan(default_apiserver, int(default_port)) == 'closed':
        sys.exit("No connection to API server")
    '''
    choices = list()
    create_url = 'http://' + default_apiserver + ':' + default_port + '/api/' + product + '/create/'  # noqa
    response = requests.options(create_url)

    # FIXME: Call is made multiple times. Can this be reduced?
    if product_meta == 'environment_type':
        environment_types = response.json()['actions']['POST']['environment_type']['choices']  # noqa
        for env in environment_types:
            choices.append(env['value'])
        return(choices)
    if product_meta == 'deployment_type':
        deployment_types = response.json()['actions']['POST']['deployment_type']['choices']  # noqa
        for env in deployment_types:
            choices.append(env['value'])
        return(choices)
    if product_meta == 'virtual_appliance':
        appliance_types = response.json()['actions']['POST']['virtual_appliance']['choices']  # noqa
        for env in appliance_types:
            choices.append(env['value'])
        return(choices)


if __name__ == '__main__':
    print(get_choices('rhos', 'deployment_type'))
    print(get_choices('rhos', 'environment_type'))
    print(get_choices('cfme', 'virtual_appliance'))
