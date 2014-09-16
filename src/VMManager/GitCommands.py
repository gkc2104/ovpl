import Logging
import os
import shlex
import subprocess
import json

class LabSpecInvalid(Exception):
    def __init__(self, msg):
        Exception(self, msg)


def repo_exists(repo_name,GIT_CLONE_LOC,lab_src_url,LAB_SPEC_LOC,source):
    Logging.LOGGER.debug("%s: repo_exists()" % (source))
    return os.path.isdir(GIT_CLONE_LOC+repo_name)

def clone_repo(repo_name,GIT_CLONE_LOC,lab_src_url,LAB_SPEC_LOC,source):
    Logging.LOGGER.debug("%s, clone_repo(): git clone %s %s%s" % (source,lab_src_url, GIT_CLONE_LOC, repo_name))
    git_clone_str = "git clone %s %s%s" % (lab_src_url, GIT_CLONE_LOC, repo_name) # To avoid null at the end
    clone_cmd = shlex.split(git_clone_str.encode('ascii'))
    Logging.LOGGER.debug("%s, clone_repo(): clone_cmd = %s" % (source,clone_cmd))
    try:
        subprocess.check_call(clone_cmd, stdout=Logging.LOG_FD, stderr=Logging.LOG_FD)
    except Exception, e:
        Logging.LOGGER.error("%s: clone_repo(): git clone failed: %s %s" % (source,repo_name, str(e)))
        raise e
def pull_repo(repo_name,GIT_CLONE_LOC,lab_src_url,LAB_SPEC_LOC,source):
    Logging.LOGGER.error("%s: pull_repo(), pull_cmd = %s" % (source,GIT_CLONE_LOC + repo_name))
    pull_cmd = "git --git-dir=%s/.git pull" % (GIT_CLONE_LOC + repo_name)
    Logging.LOGGER.debug(pull_cmd)
    try:
        subprocess.check_call(pull_cmd, stdout=Logging.LOG_FD, stderr=Logging.LOG_FD, shell=True)
    except Exception, e:
        Logging.LOGGER.error("%s: pull_repo(), git pull failed: %s %s" % (source,repo_name, str(e)))
        raise e
def reset_repo(repo_name,GIT_CLONE_LOC,lab_src_url,LAB_SPEC_LOC,source):
    Logging.LOGGER.error("%s: reset_repo(), reset_cmd = %s" % (source,GIT_CLONE_LOC + repo_name))
    reset_cmd = "git --git-dir=%s/.git reset --hard" % (GIT_CLONE_LOC + repo_name)
    Logging.LOGGER.debug(reset_cmd)
    try:
        subprocess.check_call(reset_cmd, stdout=Logging.LOG_FD, stderr=Logging.LOG_FD, shell=True)
    except Exception, e:
        Logging.LOGGER.error("%s: reset_repo(), git reset failed: %s %s" % (source,repo_name, str(e)))
        raise e

def checkout_version(repo_name,GIT_CLONE_LOC,lab_src_url,LAB_SPEC_LOC,source,version):
    Logging.LOGGER.error("%s: checkout_version(), repo_name = %s" % (source,repo_name))
    if version:
        try:
            checkout_cmd = shlex.split("git --git-dir=%s checkout %s" \
                                    % ((GIT_CLONE_LOC + repo_name), version))
            subprocess.check_call(checkout_cmd, stdout=Logging.LOG_FD, stderr=Logging.LOG_FD)
        except Exception, e:
            Logging.LOGGER.error("git checkout failed for repo %s tag %s: %s" \
                                    % (repo_name, version, str(e)))
            raise e
def get_lab_spec(repo_name,GIT_CLONE_LOC,lab_src_url,LAB_SPEC_LOC,source):
    Logging.LOGGER.error("%s: get_lab_spec(); repo_name = %s" % (source,repo_name))
    # Allow no lab spec but not an invalid json as a lab spec
    spec_path = GIT_CLONE_LOC + repo_name + LAB_SPEC_LOC
    if not os.path.exists(spec_path):
        Logging.LOGGER.error("%s: get_lab_spec(); Lab spec file not found" % (source))
        raise LabSpecInvalid("Lab spec file not found")
    try:
        return json.loads(open(spec_path).read())
    except Exception, e:
        Logging.LOGGER.error("%s: get_lab_spec(); Lab spec JSON invalid: %s "%((source) + str(e),spec_path))
        raise LabSpecInvalid("Lab spec JSON invalid: " + str(e))
