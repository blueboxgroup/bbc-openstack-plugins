# Copyright (c) 2012 OpenStack Foundation
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

from oslo_log import log as logging
from oslo_config import cfg

import nova.conf
from nova.i18n import _LW
from nova.scheduler import filters
from nova.scheduler.filters import utils

LOG = logging.getLogger(__name__)

CONF = nova.conf.CONF
reserved_host_disk_ratio = cfg.FloatOpt("reserved_host_disk_ratio", default=0.06)
CONF.register_opt(reserved_host_disk_ratio)
CONF(["--config-dir","/etc/nova"])

RESERVED_HOST_DISK_RATIO = CONF.reserved_host_disk_ratio

class BBCDiskFilter(filters.BaseHostFilter):
    """workaround for https://bugs.launchpad.net/nova/+bug/1593155."""

    def host_passes(self, host_state, spec_obj):
        """Filter based on disk usage."""
        requested_disk = (1024 * (spec_obj.root_gb +
                                  spec_obj.ephemeral_gb) +
                          spec_obj.swap)

        disk_mb_used = host_state.disk_mb_used
        total_usable_disk_mb = host_state.total_usable_disk_gb * 1024

        # Do not allow an instance to overcommit against itself, only against
        # other instances.  In other words, if there isn't room for even just
        # this one instance in total_usable_disk space, consider the host full.
        if total_usable_disk_mb < requested_disk:
            LOG.debug("%(host_state)s does not have %(requested_disk)s "
                      "MB usable disk space before overcommit, it only "
                      "has %(physical_disk_size)s MB.",
                      {'host_state': host_state,
                       'requested_disk': requested_disk,
                       'physical_disk_size':
                           total_usable_disk_mb})
            return False

        disk_mb_limit = total_usable_disk_mb * (1 - RESERVED_HOST_DISK_RATIO)
        usable_disk_mb = disk_mb_limit - disk_mb_used

        if not usable_disk_mb >= requested_disk:
            LOG.debug("%(host_state)s does not have %(requested_disk)s MB "
                    "usable disk, it only has %(usable_disk_mb)s MB usable "
                    "disk.", {'host_state': host_state,
                               'requested_disk': requested_disk,
                               'usable_disk_mb': usable_disk_mb})
            return False

        return True
