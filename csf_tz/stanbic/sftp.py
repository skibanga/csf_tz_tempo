import paramiko
import os
import frappe


class Paramiko:
    def __init__(self, hostname, user, key_path, port=22):
        self.hostname = hostname
        self.user = user
        self.port = port
        self.key_path = key_path
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connect()

    def connect(self):
        self.client.connect(
            self.hostname,
            port=self.port,
            username=self.user,
            key_filename=self.key_path,
            look_for_keys=False,
            allow_agent=False,
        )

    def download(self, remote_path, local_path, cleanup=False):
        create_dir_if_not_exists(local_path)
        sftp = self.client.open_sftp()
        sftp.get(remote_path, local_path)
        if cleanup:
            sftp.remove(remote_path)
        sftp.close()
        # return list of names of the files downloaded
        return os.listdir(local_path)

    def upload(self, local_path, remote_path, cleanup=False):
        create_dir_if_not_exists(local_path)
        sftp = self.client.open_sftp()
        sftp.put(local_path, remote_path)
        if cleanup:
            sftp.remove(local_path)
        sftp.close()
        # return list of names of the files uploaded
        return os.listdir(local_path)

    def close(self):
        self.client.close()

    def execute(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read().decode("utf-8"), stderr.read().decode("utf-8")


def create_dir_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_site_path():
    return frappe.get_site_path("private", "files")


def get_local_path(folders_name=[]):
    return os.path.join(get_site_path(), *folders_name)


def get_stanbank_files(settings_name):
    # get the files from the stanbic remote folder
    # download the files to the local folder

    # get the remote path
    remote_path = "/Inbox"
    # get the local path
    local_path = get_local_path(["stanbic", "inbox"])

    # get the settings
    settings = frappe.get_cached_doc("Stanbic Setting", settings_name)

    # create the paramiko object
    paramiko_obj = Paramiko(settings.sftp_url, settings.user, settings.private_key_path)

    # download the files
    files = paramiko_obj.download(remote_path, local_path, cleanup=True)

    # close the connection
    paramiko_obj.close()

    return files


def upload_stanbank_files(settings_name):
    # get the files from the local folder
    # upload the files to the stanbic remot folder

    # get the remote path
    remote_path = "/Outbox"

    # get the local path
    local_path = get_local_path(["stanbic", "outbox"])

    # get the settings
    settings = frappe.get_cached_doc("Stanbic Setting", settings_name)

    # create the paramiko object
    paramiko_obj = Paramiko(settings.sftp_url, settings.user, settings.private_key)

    # upload the files
    files = paramiko_obj.upload(local_path, remote_path, cleanup=True)

    # close the connection
    paramiko_obj.close()

    return files


def sync_stanbank_files(settings_name, is_test=False):
    # upload the files to the stanbic remot folder
    # get the files from the stanbic remot folder
    # download the files to the local folder

    # upload the files
    upload_files = upload_stanbank_files(settings_name, is_test)

    # download the files
    download_files = get_stanbank_files(settings_name, is_test)

    return upload_files, download_files


def sync_all_stanbank_files():
    # get all the settings
    settings = frappe.get_all("Stanbic Setting", filters={"enabled": 1})
    for setting in settings:
        sync_stanbank_files(setting.name, setting.is_test)
