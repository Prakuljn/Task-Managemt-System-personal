# Copyright 2013 Rackspace, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Scheduled Images interface (1.1 extension).
"""

from __future__ import print_function

import urllib

from novaclient import base
from novaclient import exceptions
from novaclient import utils

try:
    from novaclient.openstack.common import cliutils
except ImportError:
    cliutils = utils


DAYS=['sunday', 'monday', 'tuesday', 'wednesday',
      'thursday', 'friday', 'saturday']


class ScheduledImage(base.Resource):
    """Represents the settings for a scheduled image"""
    def __repr__(self):
        return "<ScheduledImage>"


class ScheduledImageManager(base.Manager):
    resource_class = ScheduledImage

    def get(self, server_id):
        """
        Get the scheduled image information for the server.

        :param server_id: The ID of the server to query for.
        :rtype: :class:`ScheduledImage`
        """
        try:
            return self._get("/servers/%s/rax-si-image-schedule" % server_id,
                             "image_schedule")
        except exceptions.NotFound:
            msg = "Scheduled images not enabled for server %s" % server_id
            raise exceptions.NotFound(404, msg)

    def disable(self, server_id):
        """
        Disable the creation of scheduled images for the server.

        :param server_id: The ID of the server to disable scheduled images for.
        """
        self._delete("/servers/%s/rax-si-image-schedule" % server_id)

    def enable(self, server_id, retention, day_of_week=None):
        """
        Enable the creation of scheduled images for the server.

        :param server_id: The ID of the server to enable scheduled images for.
        :param retention: The number of scheduled images to retain.
        :param day_of_week: If given, the day of week (0-6, 0=Sunday) to create
        a weekly schedule for. If omitted, create a daily schedule.
        :rtype: :class:`ScheduledImage`
        """
        try:
            retention_val = int(retention)
        except ValueError:
            msg = "Retention value must be an integer"
            raise exceptions.BadRequest(400, msg)

        body = {'image_schedule': {'retention': int(retention_val)}}

        if day_of_week is not None:
            day_of_week_str = str(day_of_week)
            if day_of_week_str.lower() not in DAYS:
                msg = ("Day_of_week value must be a string in %s"
                       % str(DAYS))
                raise exceptions.BadRequest(400, msg)

            body['image_schedule']['day_of_week'] = day_of_week_str

        return self._create("/servers/%s/rax-si-image-schedule" % server_id,
                            body, "image_schedule")

def _find_server(cs, server):
    """Get a server by name or ID."""
    return utils.find_resource(cs.servers, server)


@cliutils.arg('server', metavar='<server>', help='Name or ID of server.')
def do_scheduled_images_show(cs, args):
    """Show the scheduled image settings for a server"""
    server_id = _find_server(cs, args.server).id
    result = cs.rax_scheduled_images_python_novaclient_ext.get(server_id)
    day_of_week = getattr(result, 'day_of_week', None)
    schedule_type = 'Daily'
    if day_of_week is not None:
        schedule_type = 'Weekly on: %s' % day_of_week
    print("Schedule type: %s" % schedule_type)
    print("Retention: %s" % result.retention)


@cliutils.arg('server', metavar='<server>', help='Name or ID of server.')
@cliutils.arg('retention', metavar='<retention>', type=int,
           help='Number of scheduled images to retain')
@cliutils.arg('--day-of-week', default=None, metavar='day',
           help='If given, the day of week to create a weekly schedule '
                'for. If omitted, create a daily schedule. Valid values are: '
                '%s' % str(DAYS))
def do_scheduled_images_enable(cs, args):
    """Enable scheduled images for a server"""
    day_of_week = args.day_of_week
    if day_of_week is not None:
        day_of_week = day_of_week.lower()
    server_id = _find_server(cs, args.server).id
    result = cs.rax_scheduled_images_python_novaclient_ext.enable(
        server_id, args.retention, day_of_week=day_of_week)


@cliutils.arg('server', metavar='<server>', help='Name or ID of server.')
def do_scheduled_images_disable(cs, args):
    """Disable scheduled images for a server"""
    server_id = _find_server(cs, args.server).id
    result = cs.rax_scheduled_images_python_novaclient_ext.disable(server_id)
