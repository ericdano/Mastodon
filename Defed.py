from mastodon import Mastodon, MastodonError
import pandas as pd
import os, sys

'''

# Original -> Masto Defederation tool by Clarjon1!
# Public domain code, remix and do as ye will. Please be kind!

From your command line, 

python Defed.py csvfilename.csv

Format of the CSV
domain,severity,private_comment,public_comment
Example would be
domain,severity,private_comment,public_comment
pieville.net,suspend,taken from a.rathersafe.space,"anti semitism, national socialism, racism, ableism, HomoMisia"

This will currently update statuses if they are in your instance, so you can add public/private stuff or update if it is systemed or slienced or noop, OR add them if they are not in there.

Enjoy!
'''

def LoadCSV(defederation_csv_filename):
    DefederationList = pd.read_csv(defederation_csv_filename)
    return DefederationList

def ProcessDomains(BlockList):
    ## Access Token
    mytoken = "TOKEN"
    ### Instance URL
    myinstance = "mydomain.social"
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
    blocks1 = m.admin_domain_blocks()
    listofallblocks = m.fetch_remaining(blocks1)
    listof = pd.DataFrame(listofallblocks)
    # convert to Pandas cuz Pandas is kwel
    for i in BlockList.index:
        # first see if the domain is already in there, and if so, update it
        panda_row = listof[listof['domain'] == BlockList['domain'][i]].index.to_numpy()
        if panda_row.size > 0:
            print('Updating Status Domain->' + str(BlockList['domain'][i]) + ' Severity->' + str(BlockList['severity'][i]) + ' Private_Comment->' + str(BlockList['private_comment'][i]) + ' Public_comment->' + str(BlockList['public_comment'][i]))
            try:
                m.admin_update_domain_block(id=int(listof.iloc[panda_row]['id']),
                                            severity=BlockList['severity'][i],
                                            private_comment=BlockList['private_comment'][i],
                                            public_comment=BlockList['public_comment'][i])
            except MastodonError as e:
                print(e)
        else:
            #ok not in instance, so lets add it
            print('Adding Domain->' + str(BlockList['domain'][i]) + ' Severity->' + str(BlockList['severity'][i]) + ' Private_Comment->' + str(BlockList['private_comment'][i]) + ' Public_comment->' + str(BlockList['public_comment'][i]))
            try:
                m.admin_create_domain_block(domain=str(BlockList['domain'][i]), 
                                            severity=BlockList['severity'][i],
                                            private_comment=BlockList['private_comment'][i],
                                            public_comment=BlockList['public_comment'][i])
            except MastodonError as e:
                print(e)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Need a csv filename')
        sys.exit()
    BlockList = LoadCSV(sys.argv[1])
    ProcessDomains(BlockList)

