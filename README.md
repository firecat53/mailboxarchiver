# Gmail Archive

Combine the archivemail and gmaillabelpurge projects to archive old gmail to a
gzipped file and then delete it from Gmail's servers. The imap portion of
archivemail is removed so only local mail files can be managed.

## Prerequisites and Initial Condiditions

- Python 3
- IMAP support enabled in the Gmail account
- Maildir or Mbox files on the local computer that are managed by offlineimap or
  mbsync.
