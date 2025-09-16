# Copyright 2015 Rackspace Hosting Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from novaclient import base, utils
from novaclient import utils


class IPAssociation(base.Resource):
    def delete(self):
        self.manager.delete(ip_association=self)


class IPAssociationManager(base.ManagerWithFind):
    resource_class = base.Resource

    def list(self, server):
        return self._list('/servers/%s/ip_associations' % base.getid(server),
                          'ip_associations')

    def get(self, server, ip_association):
        return self._get('/servers/%s/ip_associations/%s' % (
            base.getid(server), base.getid(ip_association)),
            'ip_association')

    def delete(self, server, ip_association):
        self._delete('/servers/%s/ip_associations/%s' % (
            base.getid(server), base.getid(ip_association)))

    def create(self, server, ip_association):
        body = {'ip_association': {}}
        # idempotent PUT
        response = self._update(
            '/servers/%s/ip_associations/%s' % (
                base.getid(server), base.getid(ip_association)),
            body,
            'ip_association')
        return response


@utils.arg('instance_id',
              metavar='<instance_id>',
              help='ID of instance')
@utils.arg('ip_association_id',
              metavar='<ip_association_id>',
              help='ID of IP association')
def do_ip_association(cs, args):
    """
    Show an IP association
    """
    ip_association = cs.ip_associations_python_novaclient_ext.get(
        args.instance_id, args.ip_association_id)
    utils.print_dict(ip_association._info)


do_ip_association_show = do_ip_association


@utils.arg('instance_id',
              metavar='<instance_id>',
              help='ID of instance')
def do_ip_association_list(cs, args):
    """
    List IP associations
    """
    ip_associations = cs.ip_associations_python_novaclient_ext.list(
        args.instance_id)
    utils.print_list(ip_associations, ['ID', 'Address'])


@utils.arg('instance_id',
              metavar='<instance_id>',
              help='ID of instance')
@utils.arg('ip_association_id',
              metavar='<ip_association_id>',
              help='ID of IP association')
def do_ip_association_create(cs, args):
    """
    Create an IP association
    """
    ip_association = cs.ip_associations_python_novaclient_ext.create(
        args.instance_id,
        args.ip_association_id)
    utils.print_dict(ip_association._info)


@utils.arg('instance_id',
              metavar='<instance_id>',
              help='ID of instance')
@utils.arg('ip_association_id',
              metavar='<ip_association_id>',
              help='ID of IP association')
def do_ip_association_delete(cs, args):
    """
    Delete an IP association
    """
    cs.ip_associations_python_novaclient_ext.delete(
        args.instance_id, args.ip_association_id)
