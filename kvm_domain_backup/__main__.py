#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import libvirt
import os
import os.path
import sys
from argparse import ArgumentParser


class hypervisor:
    def __init__(self, credentials):
        self.domains = {}
        self._cnx = None
        self._cred = credentials
        self.catchExcpts = ['libvirtError']
        return

    def __enter__(self):
        return self

    def __exit__(self, xcpType, xcpValue, traceback):
        if self._cnx is not None:
            self._cnx.close()
        if xcpType is not None:
            if xcpType.__name__ in self.catchExcpts:
                print("[%s]: %s" % (xcpType.__name__, xcpValue))
                return True
        return

    def connect(self):
        user = self._cred["User"]
        keyfile = self._cred["Key"]
        host = self._cred["Host"]
        uri = "qemu+ssh://%s@%s/system" % (user, host)
        if os.path.isfile(keyfile):
            uri = "%s?keyfile=%s" % (uri, keyfile)
        self._cnx = libvirt.openReadOnly(uri)
        return

    def get_domains(self):
        dom_objs = self._cnx.listAllDomains(1)
        for dom in dom_objs:
            self.domains[dom.name()] = dom
        return

    def get_xml(self, domain):
        if self.is_domain(domain):
            return self.domains[domain].XMLDesc(0)
        return None

    def is_domain(self, domain):
        if domain in self.domains.keys():
            return True
        return False

    def startup(self):
        self.connect()
        self.get_domains()
        return


class backup_tree:
    def __init__(self, parent):
        if not os.path.isdir(parent):
            raise IOError('"%s": No such directory' % parent)
        self.parent = parent
        self.lostdir = '%s/lost' % parent
        if not os.path.isdir(self.lostdir):
            os.mkdir(self.lostdir)
        return

    def backup(self, domain, hv, data):
        dst_dir = '%s/%s' % (self.parent, hv)
        if not os.path.isdir(dst_dir):
            os.mkdir(dst_dir)
        with open('%s/%s.xml' % (dst_dir, domain), 'w') as config:
            config.write(data)
            self.purge_old('%s/%s.xml' % (dst_dir, domain))
        return

    def cleanup(self, directory, verbose=False):
        if verbose:
            print("Cleanup:")
        src_dir = "%s/%s" % (self.parent, directory)
        dst_dir = "%s/%s" % (self.lostdir, directory)
        if not os.path.isdir(dst_dir):
            os.mkdir(dst_dir)
        for leaf in self.get_tree(src_dir):
            if leaf.find('.xml', -4) != -1:
                dst = '%s/%s' % (dst_dir, os.path.basename(leaf))
                src = '%s/%s' % (src_dir, leaf)
                if os.path.isfile(dst):
                    if verbose:
                        print(" [rm]: %s" % dst)
                    os.unlink(dst)
                else:
                    if verbose:
                        print(" [mv]: %s -> %s" % (src, dst))
                    os.rename(src, dst)
        return

    def get_tree(self, root):
        tree = []
        if os.path.isdir(root):
            for f in os.listdir(root):
                if os.path.isdir(f):
                    for fc in self.get_tree(f):
                        tree.append('%s/%s' % (f, fc))
                else:
                    tree.append(f)
        else:
            tree.append(root)
        return tree

    def purge_old(self, filename):
        target = '%s/%s' % (self.lostdir, filename)
        if os.path.isfile(target):
            os.unlink(target)
        return


def main():
    hlpDsc = "Backup libvirt domains to local XML files"
    optParser = ArgumentParser(description=hlpDsc)
    optParser.add_argument('bck_dir', help="Backup directory",
                           metavar='backup-dir', nargs='?',
                           type=str, default='.')
    optParser.add_argument('-c', '--config', help="Configuration file",
                           metavar='config-file', type=str,
                           required=True, dest='config')
    optParser.add_argument('-v', '--verbose', help="verbose",
                           action='store_true', required=False,
                           default=False)
    try:
        args = optParser.parse_args()
    except IOError as ioe:
        print("%s: %s" % (ioe.filename, ioe.strerror))
        sys.exit(1)
    if not os.path.isfile(args.config):
        print("%s: File not found")
        sys.exit(2)
    with open(args.config, 'r') as cf:
        config = json.loads(cf.read())
    try:
        bck = backup_tree(args.bck_dir)
    except IOError as ioe:
        print("Cannot create backup_tree")
        print(ioe.message)
        sys.exit(3)
    if args.verbose:
        print("Starting backup process:")
        print(args.bck_dir)
    for hv in config['Hypervisor']:
        if args.verbose:
            print("|- %s/" % hv)
        cnx_data = {"Host": hv}
        cnx_data.update(config["Account"])
        with hypervisor(cnx_data) as kvm:
            kvm.startup()
            bck.cleanup(hv)
            for dom in kvm.domains.keys():
                if args.verbose:
                    print("   |- %s.xml" % dom)
                bck.backup(dom, hv, kvm.get_xml(dom))
    return


if __name__ == "__main__":
    main()
