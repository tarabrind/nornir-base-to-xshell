import os
import shutil

from jinja2 import Template
from nornir import InitNornir

import conf


def main():
    nr = InitNornir(config_file="network_data/nornir_conf.yaml")

    with open("template.jinja2", "r", encoding="utf-16") as file:
        template = file.read()
    jinja_template = Template(template)

    current_dir = "xshell"
    if os.path.isdir(current_dir):
        shutil.rmtree(current_dir)
    user_dir = current_dir

    for user in conf.LOGINS:
        current_dir = user_dir + "/" + user
        root_dir = current_dir

        placements = [item for item in nr.inventory.groups['placement'].groups]
        for placement in placements:
            nr_placement = nr.filter(placement=placement.name)
            current_dir = root_dir + "/" + placement['description']
            placement_dir = current_dir

            branches = [item for item in nr.inventory.groups['branch'].groups]
            for branch in branches:
                nr_branches = nr_placement.filter(branch=branch.name)
                current_dir = placement_dir + "/" + branch['description']
                branch_dir = current_dir

                sybsystems = [
                    item for item in nr.inventory.groups['subsystem'].groups]
                for subsystem in sybsystems:
                    nr_filtered = nr_branches.filter(subsystem=subsystem.name)
                    current_dir = branch_dir + "/" + subsystem['description']

                    for nr_host in nr_filtered.inventory.hosts:
                        result = jinja_template.render(
                            host=nr_filtered.inventory.hosts[nr_host].hostname,
                            port="22",
                            protocol="SSH",
                            username=user,
                            description=nr_filtered.inventory.hosts[nr_host]['old_name'],
                        )
                        os.makedirs(current_dir, exist_ok=True)
                        filename = current_dir + "/" + nr_host + ".xsh"
                        with open(filename, "w", encoding="utf-16") as file:
                            file.write(result)


if __name__ == "__main__":
    main()
