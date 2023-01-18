from mastodon import Mastodon, MastodonError
import pandas as pd
import os, sys, json
from pathlib import Path

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

Added a .json configuration file, it lives in your home directory, .MastodonAPI/appkey.json

This version will download the latest blocklist of your choosing from https://github.com/sgrigson/oliphant/tree/main/blocklists


df = pd.read_csv('https://raw.githubusercontent.com/scpike/us-state-county-zip/master/geo-data.csv')

Commandline to pick which list you want is coming shortly.

Enjoy!
'''
def LoadCSV(defederation_csv_filename):
    DefederationList = pd.read_csv(defederation_csv_filename)
    return DefederationList

def ConnectToMastodon(AccessToken,MastodonDomain):
    ## Access Token
    mytoken = AccessToken
    ### Instance URL
    myinstance = MastodonDomain
    print(mytoken)
    print(myinstance)
    m = Mastodon(access_token=mytoken, api_base_url=myinstance)
    return m

def RemoveInstancesFromBlocklist(m_instance,BlockList,allblocks):
    '''
    Do a little bit of pandas magic to find the sites that are not in the current block list. 
    Then we go delete them
    '''
    toremove_all = allblocks.merge(BlockList.drop_duplicates(), on=['domain'], how='left', indicator=True)
    toremove = toremove_all[toremove_all['_merge'] == 'left_only']
    print(toremove)
    #str(BlockList['domain'][i]), 
    for i in toremove.index:
        try:
            m_instance.admin_delete_domain_block(id=int(toremove['id'][i]))
            print('Deleted->' + str(toremove['domain'][i]) + ' id->' + str(toremove['id'][i]))
        except MastodonError as e:
            print(e)

def GetAllBlocks(m_instance):
    blocks1 = m_instance.admin_domain_blocks()
    listofallblocks = m_instance.fetch_remaining(blocks1)
    listof = pd.DataFrame(listofallblocks)
    return listof

def ProcessDomains2(BlockList,currentblocks):
    print(BlockList)
    print(currentblocks)
    '''
    This one finds things not in current block list. So new additions coming from csv
    df_all = BlockList.merge(currentblocks.drop_duplicates(), on = ['domain','severity','reject_reports','reject_media','obfuscate'], how='left', indicator=True)
    '''
    df_all = currentblocks.merge(BlockList.drop_duplicates(), on = ['domain','severity','reject_reports','reject_media','obfuscate'], how='left', indicator=True)
    print('----DF All------------')
    print(df_all)
    print('-----DF Merge-------')
    print(df_all.loc[df_all['_merge'] != 'left_only'])
    df2_all = BlockList.merge(currentblocks.drop_duplicates(), on = ['domain','severity','reject_reports','reject_media','obfuscate'], how='left', indicator=True)
    print('-----DF2 All-------')
    print(df2_all)
    print('-----DF2 Merge-------')
    print(df2_all.loc[df2_all['_merge'] != 'left_only'])

def ProcessDomains(m_instance,BlockList,listof):

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

    # convert to Pandas cuz Pandas is kwel
    for i in BlockList.index:
        # first see if the domain is already in there, and if so, update it
        #listof = listof.replace(np.nan,None)
        panda_row = listof[listof['domain'] == BlockList['domain'][i]].index.to_numpy()
        if panda_row.size > 0:
            print('Updating Status Domain->' + str(BlockList['domain'][i]) + ' Severity->' + str(BlockList['severity'][i]) + ' Public_comment->' + str(BlockList['public_comment'][i]))
            try:
                m_instance.admin_update_domain_block(id=int(listof.iloc[panda_row]['id']),
                                            severity=BlockList['severity'][i],
                                            public_comment="",
                                            #private_comment=BlockList['private_comment'][i],
                                            #public_comment=BlockList['public_comment'][i],
                                            reject_media=BlockList['reject_media'][i],
                                            reject_reports=BlockList['reject_reports'][i],
                                            obfuscate=BlockList['obfuscate'][i])
            except MastodonError as e:
                print(e)
        else:
            #ok not in instance, so lets add it
            print('Adding Domain->' + str(BlockList['domain'][i]) + ' Severity->' + str(BlockList['severity'][i]) + ' Public_comment->' + str(BlockList['public_comment'][i]))
            try:
                m_instance.admin_create_domain_block(domain=str(BlockList['domain'][i]), 
                                            severity=BlockList['severity'][i],
                                            #private_comment=BlockList['private_comment'][i],
                                            public_comment='',
                                            #public_comment=BlockList['public_comment'][i],
                                            reject_media=BlockList['reject_media'][i],
                                            reject_reports=BlockList['reject_reports'][i],
                                            obfuscate=BlockList['obfuscate'][i])
            except MastodonError as e:
                print(e)

if __name__ == '__main__':
    '''
    if len(sys.argv) < 2:
        print('You Need to specify a BlockList')
        sys.exit()
    else
        thelists = pd.DataFrame([{'unified_max_blocklist':'https://github.com/sgrigson/oliphant/blob/main/blocklists/_unified_max_blocklist.csv',
                                'unified_min_blocklist':'https://github.com/sgrigson/oliphant/blob/main/blocklists/_unified_min_blocklist.csv',
                                'unified_tier0_blocklist':'https://github.com/sgrigson/oliphant/blob/main/blocklists/_unified_tier0_blocklist.csv',
                                'unified_tier1_blocklist':'https://github.com/sgrigson/oliphant/blob/main/blocklists/_unified_tier1_blocklist.csv',
                                'unified_tier2_blocklist':'https://github.com/sgrigson/oliphant/blob/main/blocklists/_unified_tier2_blocklist.csv',
                                'unified_tier3_blocklist':'https://github.com/sgrigson/oliphant/blob/main/blocklists/_unified_tier3_blocklist.csv',
                                'artisan.chat':'https://github.com/sgrigson/oliphant/blob/main/blocklists/artisan.chat.csv',
                                'rapidblock.org-blocklist':'https://github.com/sgrigson/oliphant/blob/main/blocklists/https:--rapidblock.org-blocklist.json.csv',
                                'mastodon.art':'https://github.com/sgrigson/oliphant/blob/main/blocklists/mastodon.art.csv',
                                'mastodon.online':'https://github.com/sgrigson/oliphant/blob/main/blocklists/mastodon.online.csv',
                                'mastodon.social':'https://github.com/sgrigson/oliphant/blob/main/blocklists/mastodon.social.csv',
                                'oliphant.social':'https://github.com/sgrigson/oliphant/blob/main/blocklists/oliphant.social.csv',
                                'rage.love':'https://github.com/sgrigson/oliphant/blob/main/blocklists/rage.love.csv',
                                'toot.wales':'https://github.com/sgrigson/oliphant/blob/main/blocklists/toot.wales.csv',
                                'union.place':"https://github.com/sgrigson/oliphant/blob/main/blocklists/union.place.csv"}])
        for i in thelists.index:
            # first see if the domain is already in there, and if so, update it
            pd_row = listof[listof['domain'] == BlockList['domain'][i]].index.to_numpy()
'''
    home = Path.home() / ".MastodonAPI" / "appkey.json"
    confighome = Path.home() / ".MastodonAPI" / "appkey.json"
    with open(confighome) as f:
        configs = json.load(f)
        #BlockList = LoadCSV(sys.argv[1])
    BlockList = pd.read_csv('https://raw.githubusercontent.com/sgrigson/oliphant/main/blocklists/_unified_min_blocklist.csv')
    m_instance = ConnectToMastodon(configs['MastodonAccessToken'],configs['MastodonDomain'])
    allblocks = GetAllBlocks(m_instance)
    RemoveInstancesFromBlocklist(m_instance,BlockList,allblocks)
    #ProcessDomains2(BlockList,allblocks)
    ProcessDomains(m_instance,BlockList,allblocks)

