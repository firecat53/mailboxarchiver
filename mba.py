#!/usr/bin/env python

""" Archive old gmail from a local maildir or mbox store to a compressed file.
  Also delete the archived mail from Gmail's servers

 - Read mailbox `Maildir(path)`
 - Uncompress and open backup file (mbox format)
 - Iterate through mailbox messages:
   - If not in backup, add it
   - If it is, skip it
 - Compress backup
 - Delete messages with that mailbox name from Gmail
   - Use modified gmaillabelpurge.py script"""

import argparse
from contextlib import contextmanager
from datetime import date
import email
import logging
from mailbox import Maildir, mbox
from os.path import expanduser, join
import re

from dateutil import parser, relativedelta

@contextmanager
def open_box(aname, mailbox):
    """Uncompress and open backup file. Create if doesn't exist

    Args: aname - backup filename
          mailbox - path to mailbox
    """
    try:
        # Uncompress first
        backup_box = mbox(aname)
        backup_box.lock()
        # maildir doesn't require locking
        box = Maildir(mailbox)
        yield backup_box, box
    except Exception:
        raise
    finally:
        backup_box.unlock()
        close_backup(aname)


def close_backup(aname):
    """Close and compress backup file

    Args: aname - name of backup file

    """
    pass


def backup_mail(bbox, mailbox, days):
    """Iterate through mailbox messages and add to backup file

    Args: bbox - mailbox.mbox (backup target)
          mailbox - mailbox.Maildir (source)
          days - days of mail to retain

    """
    ids = [i['Message-Id'] for i in bbox]
    bad_date = re.compile(r'(^.*\([A-Z]{3})([\+\- ][0-9]{0,2})\)')
    tdate = date.today() + relativedelta.relativedelta(days=-days)
    errs = []
    for key in mailbox.iterkeys():
        # First make sure message is parsed correctly
        try:
            msg = mailbox[key]
        except email.errors.MessageParseError as err:
            errs.append((key, err))
            continue
        try:
            mdate = parser.parse(msg['Date'])
        except parser.ParserError:
            # Fix for error I found in some of my email date strings
            tmp = re.sub(bad_date, r"\1)", msg['Date'])
            try:
                mdate = parser.parse(tmp)
            except parser.ParserError as err:
                errs.append((key, err))
                continue
        if msg['Message-Id'] not in ids and mdate.date() < tdate:
            bbox.add(msg)
    return errs


def parse_arguments():
    """Parse command line arguments

    """
    arg_parse = argparse.ArgumentParser(description="Archive gmail older than x days")
    arg_parse.add_argument('--days', '-d',
                           type=int, default=180,
                           help="Archive mail older than x days")
    arg_parse.add_argument('--archive-name', '-a', dest='aname',
                           default="mail_archive",
                           help="Name/path of mail archive backup file")
    arg_parse.add_argument('--mailbox-path', '-p', dest='mailbox',
                           default=".",
                           help="Path to maildirs")
    arg_parse.add_argument('--folders', '-f',
                           nargs='+', default=["INBOX"],
                           help="Space separated list of folders to archive")
    args = arg_parse.parse_args()
    return args


def run():
    """Script entrypoint

    """
    args = parse_arguments()
    for folder in args.folders:
        path = join(expanduser(args.mailbox), folder)
        with open_box(expanduser(args.aname), path) as (backup_box, inbox):
            errs = backup_mail(backup_box, inbox, args.days)
    print(errs)
if __name__ == "__main__":
    run()
