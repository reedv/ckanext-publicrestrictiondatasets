import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging

from ckan import model


class PublicrestrictiondatasetsPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)

    # IConfigurer
    
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic',
            'publicrestrictiondatasets')


    # IDatasetForm

    def _sysadmins_only_create(self, value, context):
        # ensure that only sysadmins can create public packages
        log = logging.getLogger(__name__)
        
        log.debug('\n=====publicrestrictiondatasets:_sysadmins_only_create(value, context)=====')
        log.debug(value)
        log.debug(type(value))
        log.debug([m for m in dir(value) if not m.startswith('__')])
        log.debug(context)
        log.debug(type(context))
        log.debug([m for m in dir(context) if not m.startswith('__')])
        log.debug(type(context.get('package')))
        log.debug([m for m in dir(context.get('package')) if not m.startswith('__')])

        username = context.get('user')
        user = model.User.get(username)
        private = value
        if (not private) and (not user.sysadmin):
            raise toolkit.Invalid('Only sysadmin users may set datasets as public')
        else:
            return value

    def _sysadmins_only_update(self, value, context):
        # ensure that only sysadmins can update packages' visibility status from private to public (but editors can still make other changes to already-public packages)
        log = logging.getLogger(__name__)

        log.debug('\n=====publicrestrictiondatasets:_sysadmins_only_update(value, context)=====')
        log.debug(value)
        log.debug(type(value))
        log.debug([m for m in dir(value) if not m.startswith('__')])
        log.debug(context)
        log.debug(type(context))
        log.debug([m for m in dir(context) if not m.startswith('__')])
        log.debug(type(context.get('package')))
        log.debug([m for m in dir(context.get('package')) if not m.startswith('__')])

        package = context.get('package')  # model representing the old values of the package
        username = context.get('user')
        user = model.User.get(username)
        private = value
        if (not private) and (not user.sysadmin) and (private != package.private):
            raise toolkit.Invalid('Only sysadmin users may set datasets as public')
        else:
            return value

#    def _modify_package_schema(self, schema):
#        log = logging.getLogger(__name__)
#        log.debug('\n=====publicrestrictiondatasets:_modify_package_schema(self, schema)=====')
#        log.debug(schema)
#
#        schema.update({
#            # our validator must come last, so the boolean_validator can execute first and convert value to bool
#            'private': schema['private'] + [self._sysadmins_only]  #[toolkit.get_validator('ignore_not_sysadmin')]
#        })
#        return schema

    def create_package_schema(self):
        # let's grab the default schema in our plugin
        schema = super(PublicrestrictiondatasetsPlugin, self).create_package_schema()
        
        schema.update({
            # our validator must come last, so the boolean_validator can execute first and convert value to bool
            'private': schema['private'] + [self._sysadmins_only_create]  #[toolkit.get_validator('ignore_not_sysadmin')]
        })
        return schema

    def update_package_schema(self):
        schema = super(PublicrestrictiondatasetsPlugin, self).update_package_schema()
        
        schema.update({
            # our validator must come last, so the boolean_validator can execute first and convert value to bool
            'private': schema['private'] + [self._sysadmins_only_update]  #[toolkit.get_validator('ignore_not_sysadmin')]
        })
        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []


