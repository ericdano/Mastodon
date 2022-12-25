# Masto Defederation tool by Clarjon1!
# Public domain code, remix and do as ye will. Please be kind!

from mastodon import Mastodon
import pandas as pd
import os, sys

######
## VARIABLES EDITINGS

#
### Defed List File Name.
### Action to take. Current valid options: suspend, silence, limit


def LoadCSV(defederation_csv_filename):
    DefederationList = pd.read_csv(defederation_csv_filename)
    return DefederationList

def ProcessDomains(BlockList):
    ## Access Token
    mytoken = ""
    ### Instance URL
    myinstance = ""
    '''
    Example from API
    [
  {
    "id": "1",
    "domain": "example.com",
    "created_at": "2022-11-16T08:15:34.238Z",
    "severity": "noop",
    "reject_media": false,
    "reject_reports": false,
    "private_comment": null,
    "public_comment": null,
    "obfuscate": false
  },
    '''
    m = Mastodon(access_token=mytoken, api_base_url=myinstance)
    print(m)
    for i in BlockList.index:
        print('Blocking Domain->' + str(BlockList['domain'][i]) + ' Severity->' + str(BlockList['severity'][i]) + ' Private_Comment->' + str(BlockList['private_comment'][i]) + ' Public_comment->' + str(BlockList['public_comment'][i]))
        m.admin_create_domain_block(domain=str(BlockList['domain'][i]), 
                                    severity=BlockList['severity'][i],
                                    private_comment=BlockList['private_comment'][i],
                                    public_comment=BlockList['public_comment'][i])
 
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Need a csv filename')
        sys.exit()
    BlockList = LoadCSV(sys.argv[1])
    ProcessDomains(BlockList)

