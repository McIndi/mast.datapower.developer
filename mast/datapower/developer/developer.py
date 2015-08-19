"""==========================================================
mast dev:

A set of tools for automating routine development
tasks associated with IBM DataPower appliances.

Copyright 2014, All Rights Reserved
McIndi Solutions LLC
=========================================================="""
import os
import commandr
from mast.logging import make_logger, logged
import mast.plugin_utils.plugin_utils as util
from mast.datapower import datapower
from mast.timestamp import Timestamp

cli = commandr.Commandr()

# Caches
# ======
#
# These functions are meant to be used to flush the caches that DataPower
# maintains.
#
# Current Commands:
# ----------------
#
# FlushDocumentCache(XMLManager)
# FlushStylesheetCache(XMLManager)
#


@logged("mast.datapower.developer")
@cli.command('flush-document-cache', category='caches')
def flush_document_cache(appliances=[], credentials=[],
                         timeout=120, Domain="", xml_manager="",
                         no_check_hostname=False, web=False):
    """Flushes the Document Cache for the specified xml_manager
in the specified domain.

Parameters:

* Domain - The domain where xml_manager resides
* xml_manager - The XMLManager who's cache to flush'"""
    logger = make_logger("mast.developer")
    check_hostname = not no_check_hostname
    env = datapower.Environment(
        appliances,
        credentials,
        timeout,
        check_hostname=check_hostname)
    logger.info(
        "Attempting to flush document cache for {} in {} domain on {} XMLManager".format(
            str(env.appliances), Domain, xml_manager))

    kwargs = {"XMLManager": xml_manager, 'domain': Domain}
    responses = env.perform_action('FlushDocumentCache', **kwargs)
    logger.debug("Responses received: {}".format(str(responses)))

    if web:
        return util.render_boolean_results_table(
            responses, suffix="flush_document_cache"), util.render_history(env)

    for host, response in list(responses.items()):
        if response:
            print
            print host
            print '=' * len(host)
            if response:
                print 'OK'
            else:
                print "FAILURE"
                print response


@logged("mast.datapower.developer")
@cli.command('flush-stylesheet-cache', category='caches')
def flush_stylesheet_cache(appliances=[], credentials=[],
                           timeout=120, Domain="", xml_manager="",
                           no_check_hostname=False, web=False):
    """Flushes the Stylesheet Cache for the specified xml_manager
in the specified domain.

Parameters:

* Domain - The domain where xml_manager resides
* xml_manager - The XMLManager who's cache to flush'"""
    logger = make_logger("mast.developer")
    check_hostname = not no_check_hostname
    env = datapower.Environment(
        appliances,
        credentials,
        timeout,
        check_hostname=check_hostname)
    logger.info(
        "Attempting to flush stylesheet cache for {} in {} domain on {} XMLManager".format(
            str(env.appliances), Domain, xml_manager))

    kwargs = {"XMLManager": xml_manager, 'domain': Domain}
    responses = env.perform_action('FlushStylesheetCache', **kwargs)
    logger.debug("Responses received: {}".format(str(responses)))

    if web:
        return util.render_boolean_results_table(
            responses,
            suffix="flush_stylesheet_cache"), util.render_history(env)

    for host, response in list(responses.items()):
        if response:
            print
            print host
            print '=' * len(host)
            if response:
                print 'OK'
            else:
                print "FAILURE"
                print response

# services/objects
# ================
#
# These functions are meant to affect the services and objects
# on the DataPower appliances
#
# current commands
# ----------------
# import - import a service or object to the specified domain
# export - export a service or object from the specified domain


@logged("mast.datapower.developer")
@cli.command('import', category='services/objects')
def _import(appliances=[], credentials=[],
            timeout=120, Domain="", file_in=None,
            deployment_policy=None, dry_run=False,
            overwrite_files=True, overwrite_objects=True,
            rewrite_local_ip=True, source_type='ZIP',
            out_dir="tmp/", no_check_hostname=False, web=False):
    """Import a service/object into the specified appliances

Parameters:

* Domain - The domain into which the configuration will be imported
* file_in - The file to import into the specified domain. This
__MUST__ match the format specified in source_type
* deployment_policy - The deployment policy to use for the import
(must already exist on the appliances)
* dry_run - Whether to do a dry-run (nothing will be imported)
* overwrite_files - Whether to overwrite files
* overwrite_objects - Whether to overwrite objects
* rewrite_local_ip - Whether to rewrite the local ip addresses in the
configuration
* source-type - The type of file to import. Can be "XML" or "ZIP" """
    logger = make_logger("mast.developer")
    t = Timestamp()

    check_hostname = not no_check_hostname
    env = datapower.Environment(
        appliances,
        credentials,
        timeout,
        check_hostname=check_hostname)
    logger.info(
        "Attempting to import {} to {}".format(
            file_in, str(env.appliances)))

    kwargs = {
        'domain': Domain,
        'zip_file': file_in,
        'deployment_policy': deployment_policy,
        'dry_run': dry_run,
        'overwrite_files': overwrite_files,
        'overwrite_objects': overwrite_objects,
        'rewrite_local_ip': rewrite_local_ip,
        'source_type': source_type}

    results = env.perform_action('do_import', **kwargs)
    logger.debug("Responses received: {}".format(str(results)))

    out_dir = os.path.join(out_dir, "import_results", t.timestamp)
    os.makedirs(out_dir)

    for host, response in results.items():
        filename = os.path.join(out_dir, "{}-import_results.xml".format(host))
        with open(filename, 'wb') as fout:
            fout.write(response.pretty)
    if web:
        return util.render_see_download_table(
            results, suffix="import"), util.render_history(env)


@logged("mast.datapower.developer")
@cli.command('export', category='services/objects')
def export(appliances=[], credentials=[],
           timeout=120, Domain="",
           object=None, object_class=None,
           comment='', format='ZIP',
           persisted=True, all_files=True,
           referenced_files=True, referenced_objects=True,
           out_dir='tmp', no_check_hostname=False, web=False):
    """Exports a service or object to be used to import into another
domain or appliance

Parameters:

* Domain - The domain from which to export service/object
* object - The name of the object to export
* object_class - The class of the object to export
* comment - The comment to embed into the export
* format - the format in which to export the configuration. This
can be either "XML" or "ZIP"
* persisted - Whether to export the persisted configuration
(if False the running configuration will be exported)
* all-files - Whether to include all referenced files in the export
* referenced_files - Whether to include the referenced files
* referenced_objects - Whether to include the referenced objects
* out_dir - (**NOT NEEDED IN THE WEB GUI**)The directory (local)
in which to save the export"""
    logger = make_logger("mast.developer")
    t = Timestamp()

    check_hostname = not no_check_hostname
    env = datapower.Environment(
        appliances,
        credentials,
        timeout,
        check_hostname=check_hostname)
    logger.info(
        "Attempting to export {} from {}".format(
            object, str(env.appliances)))

    kwargs = {
        'domain': Domain,
        'obj': object,
        'object_class': object_class,
        'comment': comment,
        'format': format,
        'persisted': persisted,
        'all_files': all_files,
        'referenced_objects': referenced_objects,
        'referenced_files': referenced_files}

    results = env.perform_action(
        'export',
        **kwargs)

    for hostname, _export in results.items():
        d = os.path.join(out_dir, hostname, t.timestamp)
        os.makedirs(d)
        filename = os.path.join(d, '%s-%s-%s.zip' % (
            t.timestamp,
            hostname,
            object))
        logger.debug("Writing export of {} from {} to {}".format(
            object, hostname, filename))
        with open(filename, 'wb') as fout:
            fout.write(_export)
    if web:
        return util.render_see_download_table(
            results, suffix="export"), util.render_history(env)


@logged("mast.datapower.developer")
def get_data_file(f):
    _root = os.path.dirname(__file__)
    path = os.path.join(_root, "data", f)
    with open(path, "rb") as fin:
        return fin.read()

from mast.plugins.web import Plugin
import mast.plugin_utils.plugin_functions as pf
from functools import partial, update_wrapper


class WebPlugin(Plugin):
    def __init__(self):
        self.route = partial(pf.handle, "developer")
        self.route.__name__ = "developer"
        self.html = partial(pf.html, "mast.datapower.developer")
        update_wrapper(self.html, pf.html)

    def css(self):
        return get_data_file('plugin.css')

    def js(self):
        return get_data_file('plugin.js')


if __name__ == '__main__':
    try:
        cli.Run()
    except AttributeError, e:
        if "'NoneType' object has no attribute 'app'" in e:
            raise NotImplementedError(
                "HTML formatted output is not supported on the CLI")

