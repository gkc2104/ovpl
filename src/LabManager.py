import json
import re
import os
import os.path
import subprocess
import shlex
from exceptions import Exception
import requests
import time
import math

import Logging
from VMManager import GitCommands
from envsetup import EnvSetUp

#GIT_CLONE_LOC = "./lab-repo-cache/"
#LAB_SPEC_LOC = "/scripts/labspec.json"
#TEST_LAB_API_URI = '/api/1.0/test-lab'

class LabSpecInvalid(Exception):
    def __init__(self, msg):
        Exception(self, msg)

def get_lab_reqs(lab_id, lab_src_url, version=None):
    e = EnvSetUp()
    Logging.LOGGER.debug("LabManager: get_lab_reqs():  Invoked from Controller")
    current_file_path = os.path.dirname(os.path.abspath(__file__))
    config_spec = json.loads(open(current_file_path + "/../config/config.json").read())
    GIT_CLONE_LOC =  config_spec["LABMANAGER_CONFIG"]["GIT_CLONE_LOC"]
    LAB_SPEC_LOC =  config_spec["LABMANAGER_CONFIG"]["LAB_SPEC_LOC"]
    Logging.LOGGER.debug("LabManager: GIT_CLONE_LOC = %s" % str(GIT_CLONE_LOC))
    Logging.LOGGER.debug("LabManager: LAB_SPEC_LOC = %s" % str(LAB_SPEC_LOC))

    # sample lab_src_url: git@github.com:vlead/ovpl.git
    def construct_repo_name(lab_id, lab_src_url):
        Logging.LOGGER.debug("LabManager: construct_repo_name()")
        repo = lab_src_url.split('/')[-1]
        repo_name = lab_id + (repo[:-4] if repo[-4:] == ".git" else repo)
        return repo_name
    
    
    repo_name = construct_repo_name(lab_id, lab_src_url,)
    if GitCommands.repo_exists(repo_name,GIT_CLONE_LOC,lab_src_url,LAB_SPEC_LOC,'LabManager()'):
        GitCommands.reset_repo(repo_name,GIT_CLONE_LOC,lab_src_url,LAB_SPEC_LOC,'LabManager()')
        GitCommands.pull_repo(repo_name,GIT_CLONE_LOC,lab_src_url,LAB_SPEC_LOC,'LabManager()')
    else:
        GitCommands.clone_repo(repo_name,GIT_CLONE_LOC,lab_src_url,LAB_SPEC_LOC,'LabManager()')

    GitCommands.checkout_version(repo_name,GIT_CLONE_LOC,lab_src_url,LAB_SPEC_LOC,'LabManager()',version)
    return GitCommands.get_lab_spec(repo_name,GIT_CLONE_LOC,lab_src_url,LAB_SPEC_LOC,'LabManager()')
    #vm_spec = json.loads(open("vmspec.json", "r").read())

def test_lab(vmmgr_ip, port, lab_src_url, version=None):
    # make sure VM Manager is running
    # the target VM should have LabActionRunner scripts 
    # VM Manager should do the following?
    # or better it should invoke another script which should
        # clone the repo in the VM
        # get the lab_spec
        # run Lab Action Runner
    if not 'http' in vmmgr_ip:
        raise Exception('Protocol not specified in VMManager host address!!')
    e = EnvSetUp()

    Logging.LOGGER.debug("LabManager.test_lab(): vmmgr_ip = %s, port = %s, lab_src_url = %s" % (vmmgr_ip, port, lab_src_url))
    payload = {"lab_src_url": lab_src_url, "version": version}
    current_file_path = os.path.dirname(os.path.abspath(__file__))
    config_spec = json.loads(open(current_file_path + "/../config/config.json").read())
    TEST_LAB_API_URI = config_spec["VMMANAGER_CONFIG"]["TEST_LAB_URI"]
    url = '%s:%s%s' % (vmmgr_ip, port, TEST_LAB_API_URI)
    Logging.LOGGER.debug("LabManager.test_lab(): url = %s, payload = %s" % (url, str(payload)))

    exception_str = ""
    for i in (1,2,4,8,16):
        time.sleep(i)
        try:
            response = requests.post(url=url, data=payload)
            Logging.LOGGER.debug("LabManager.test_lab(): response = %s" % response)
            return ("Success" in response.text, response.text)
        except Exception, e:
            exception_str = str(e)
            attempts = {0:'first', 1:'second', 2:'third', 3:'fourth'}
            Logging.LOGGER.error("LabManager.test_lab(): Error installing lab on VM for the %s attempt with error: %s" % \
                                 (attempts[math.log(i)/math.log(2)], str(e)))
    return (False, exception_str)
    
if __name__ == '__main__':
    (ret_val, ret_str) = test_lab('http://10.2.59.2', '8089', 'git@bitbucket.org:virtuallabs/cse02-programming.git')
    if (ret_val):
        print "Test Successful"
    else:
        print "Test Unsuccessful"
