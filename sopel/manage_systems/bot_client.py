import requests

from .client import RHOS


class IRCBot(RHOS):
    def all_versions(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            for entry in response.json():
                yield "|id: {} |ver: {} |Deployment: {}({}) |Host: {} |".format(entry['id'],
                                    entry['version'],
                                    entry['deployment_type'],
                                    entry['environment_type'],
                                    entry['ip_address'])


    def version(self, version=None, deployment_type=None, in_use=False):
        queryurl = "{}/?version={}&deployment_type={}&in_use={}".format(
            self.url,
            version if version else '',
            deployment_type if deployment_type else '',
            in_use)
        response = requests.get(queryurl)

        if response.status_code == 200:
            for entry in response.json():
                yield "|id: {} |ver: {} |Deployment: {}({}) |Host: {} |".format(entry['id'],
                                    entry['version'],
                                    entry['deployment_type'],
                                    entry['environment_type'],
                                    entry['ip_address'])

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
            return "|id: {} |ver: {} |Host: {} |Deployment: {}({}) |is_use: {} |used_by: {} |owner: {} |specs: {} |reserved_on: {} |State: {}|".format(
                data['id'], data['version'], data['ip_address'],
                data['environment_type'], data['deployment_type'],
                data['in_use'], data['used_by'], data['owner'],
                data['specs'], data['reserved_on'], state)
        else:
            return "Error: Invalid sys_id"

    def reserve(self, systemid, user_email):
        '''
        Reserve system with ID and email address

        Usage:
            obj.reserve(2, "pbandark@redhat.com")
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

            return "|id: {} |ver: {} |Host: {} |Username: {} |Password: {} |Status: {}|".format(data['id'], data['version'],
                            data['ip_address'],
                            data['sys_username'], data['sys_password'],
                            state)

        return resp.status_code

    def release(self, systemid):
        '''
        Release system by ID

        Usage:
            obj.release(2)
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
            return "|id: {} |ver: {} |Host: {} |Status: {}|".format(data['id'], data['version'],
                                                                    data['ip_address'], 'RELEASED')
        return response.status_code


if __name__ == '__main__':
    irc = IRCBot('10.65.223.141', '8000', 'rhos')
    for i in irc.all_versions():
        print(i)
