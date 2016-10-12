import socket
import nmap
import requests
from prettytable import PrettyTable


class ResponseError(Exception):
    pass


class Setup:
    '''
    Specify server, port and product(rhos/cfme)

    Docstring: TODO: Valid values accepted by class
    '''
    def __init__(self, server, port, product_name):
        self.server = server
        self.port = port
        self.product_name = product_name
        self.base_api = '/api/'
        self.url = 'http://' + self.server + ':' + self.port + self.base_api + product_name

    @classmethod
    def invalid_id(cls, systemid):
        table = PrettyTable(['id', 'status'])
        table.add_row([systemid, 'Invalid ID'])
        return table

    @classmethod
    def no_data(cls):
        table = PrettyTable(['Status'])
        table.add_row(['No data'])
        return table

    @classmethod
    def port_scan(cls, host, port):
        try:
            host_ip = socket.gethostbyname(host)
        except:
            host_ip = host

        scanner = nmap.PortScanner()
        scanner.scan(host_ip, str(port))
        state = scanner[host_ip]['tcp'][port]['state']
        return state

    def all_versions(self):
        '''
        Show everthing
        '''
        response = requests.get(self.url)
        if response.status_code == 200:
            table = PrettyTable(['id', 'version', 'deployment_type',
                                 'ip_address', 'environment_type',
                                 'in_use', 'used_by'])
            for entry in response.json():
                table.add_row([entry['id'], entry['version'],
                               entry['deployment_type'],
                               entry['ip_address'],
                               entry['environment_type'],
                               entry['in_use'],
                               entry['used_by'] if entry['used_by'] else '--'])
            return table
        return response.status_code


class RHOS(Setup):
    '''
    Search Red Hat OpenStack Platform based environments

    Usage:
        obj = RHOS('http://127.0.0.1', 8000 , 'rhos')
    '''
    def version(self, version=None, deployment_type=None, in_use=False):
        '''
        Search by RHOSP version

        Usage:
            obj.version(7, 'PACKSTACK')
            obj.version(7, 'PACKSTACK', in_use=True)
        '''
        queryurl = "{}/?version={}&deployment_type={}&in_use={}".format(
            self.url,
            version if version else '',
            deployment_type if deployment_type else '',
            in_use)
        response = requests.get(queryurl)

        if response.status_code == 200:
            table = PrettyTable(['id', 'version', 'deployment_type',
                                 'ip_address', 'environment_type',
                                 'in_use', 'used_by'])
            for entry in response.json():
                table.add_row([entry['id'], entry['version'],
                               entry['deployment_type'],
                               entry['ip_address'],
                               entry['environment_type'],
                               entry['in_use'],
                               entry['used_by'] if entry['used_by'] else '--'])
            return table
        return response.status_code

    def detail(self, sys_id):
        '''
        Print details about the system when searched by id

        Usage:
            obj.detail(id or pk)
            obj.detail(2)
        '''
        response = requests.get(self.url + '/' + str(sys_id))
        data = response.json()

        try:
            state = self.port_scan(data['ip_address'], 22)
        except:
            state = 'UNREACHABLE'
        if response.status_code == 200:
            table = PrettyTable(['id', 'version', 'ip_address',
                                 'environment_type', 'deployment_type',
                                 'in_use', 'used_by', 'owner', 'specs',
                                 'reserved_on', 'Port 22 status'])

            table.add_row([data['id'], data['version'], data['ip_address'],
                           data['environment_type'], data['deployment_type'],
                           data['in_use'], data['used_by'], data['owner'],
                           data['specs'], data['reserved_on'],
                           state])
            return table
        else:
            return(self.invalid_id(sys_id))

    def reserve(self, systemid, user_email):
        '''
        Reserve system with ID and email address

        Usage:
            obj.reserve_system(2, "pbandark@redhat.com")
        '''
        response = requests.get(self.url + '/' + str(systemid) + '/')
        data = response.json()

        try:
            state = self.port_scan(data['ip_address'], 22)
        except:
            state = 'UNREACHABLE'

        update = self.url + '/' + str(systemid) + '/update/'
        data = {
            "in_use": True,
            "used_by": user_email
        }
        resp = requests.patch(requests.get(update).url, data)

        if resp.status_code == 200:
            response = requests.get(self.url + '/' + str(systemid))
            data = response.json()
            table = PrettyTable(['id', 'version', 'ip_address',
                                 'sys_username', 'sys_password',
                                 'Port 22 status'])
            table.add_row([data['id'], data['version'],
                           data['ip_address'],
                           data['sys_username'], data['sys_password'],
                           state])
            return table
        return response.status_code

    def release(self, systemid):
        '''
        Release system by ID

        Usage:
            obj.release_system(2)
        '''
        response = requests.get(self.url + '/' + str(systemid) + '/')
        data = response.json()

        update = self.url + '/' + str(systemid) + '/update/'
        # FIXME: #18
        data = {
            "in_use": False,
            "used_by": ""
        }
        response = requests.patch(update, data)

        if response.status_code == 200:
            response = requests.get(self.url + '/' + str(systemid))
            data = response.json()
            table = PrettyTable(['id', 'version',
                                 'ip_address', 'status'])
            table.add_row([data['id'], data['version'],
                           data['ip_address'], 'RELEASED'])
            return table
        return response.status_code

    def delete(self, systemid):
        '''
        Delete system specifying ID
        Usage:
            obj.delete_system(2)
        '''
        response = requests.get(self.url + '/' + str(systemid) + '/')
        data = response.json()
        try:
            table = PrettyTable(['id', 'ip_address', 'status'])
            table.add_row([data['id'], data['ip_address'], 'Deleted'])
            resp = requests.delete(self.url + '/' + str(systemid) + '/delete/')
            if resp.status_code == 204:
                return table
            else:
                return(self.invalid_id(systemid))
        except KeyError:
            return(self.invalid_id(systemid))

    def add(self, version, ip_address, sys_username, sys_password,
            owner, specs, environment_type="VIRTUAL",
            deployment_type="PACKSTACK"):
        '''
        add new test system
        Usage:
             obj.add_system('5', '10.10.10.10', 'root', 'RedHat1!',
             'pbandark@redhat.com', 'test spec', 'VIRTUAL', 'HA')

            'environment_type' = 'VIRTUAL'/'PHYSICAL'
            'deployment_type' = 'HA'/'NON-HA'/'PACKSTACK'
        '''
        create = self.url + '/create/'
        data = {
            "version": version,
            "ip_address": ip_address,
            "sys_username": sys_username,
            "sys_password": sys_password,
            "environment_type": environment_type,
            "deployment_type": deployment_type,
            "owner": owner,
            "specs": specs,
        }
        requests.post(requests.get(create).url, data)
        table = PrettyTable(['ip_address', 'sys_username',
                             'sys_password', 'environment_type',
                             'deployment_type', 'owner', 'specs',
                             'Status'])
        table.add_row([ip_address, sys_username, sys_password,
                       environment_type, deployment_type, owner, specs,
                       'new system added to the database'])
        return table


if __name__ == '__main__':
    obj = RHOS('localhost', '8000', 'rhos')
    print("All version")
    print(obj.all_versions())
    print("in_use=False")
    print(obj.version())
    print("In use")
    print(obj.version(in_use=True))
    print("7")
    print(obj.version(7))
    print("7, in_use=True")
    print(obj.version(7, in_use=True))
    print("9, in_use=True")
    print(obj.version(9, in_use=True))
    print("10, HA")
    print(obj.version(10, 'HA'))
    print("9, PACKSTACK")
    print(obj.version(9, 'PACKSTACK'))
    print("7, PACKSTACK")
    print(obj.version(7, 'PACKSTACK'))
    print("7, PACKSTACK in_use=True")
    print(obj.version(7, 'PACKSTACK', in_use=True))
    print(obj.detail(1))
    print(obj.detail(3))
    print(obj.detail(26))
    print(obj.reserve(7, "pbandark@redhat.com"))
    print(obj.release(7))
    print(obj.add('5', '10.10.10.10', 'root', 'RedHat1!',
                  'pbandark@redhat.com', 'test spec'))
    print(obj.delete(2))
    print(obj.delete(6))
