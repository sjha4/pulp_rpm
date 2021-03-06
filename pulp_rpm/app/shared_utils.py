import createrepo_c
import tempfile
import shutil

from django.core.files.storage import default_storage as storage

from pulp_rpm.app.models import Package


def _prepare_package(artifact, filename):
    """
    Helper function for creating package.

    Copy file to a temp directory under
    the user provided filename.

    Returns: artifact model as dict

    Args:
        artifact: inited and validated artifact to save
        filename: name of file uploaded by user
    """
    artifact_file = storage.open(artifact.file.name)
    with tempfile.NamedTemporaryFile('wb', suffix=filename) as temp_file:
        shutil.copyfileobj(artifact_file, temp_file)
        temp_file.flush()
        cr_pkginfo = createrepo_c.package_from_rpm(temp_file.name)

    package = Package.createrepo_to_dict(cr_pkginfo)

    package['location_href'] = filename
    return package


def is_previous_revision(revision, target_revision):
    """
    Compare revision with a target revision.
    """
    if revision.isdigit() and target_revision.isdigit():
        return int(revision) <= int(target_revision)

    if "." in revision and len(revision.split(".")) == len(target_revision.split(".")):
        rev = revision.split(".")
        for index, target in enumerate(target_revision.split(".")):
            is_digit = rev[index].isdigit() and target.isdigit()
            if is_digit and int(rev[index]) < int(target):
                return True

        if is_digit:
            return int(rev[index]) <= int(target)

    if revision:
        return revision == target_revision

    return False
