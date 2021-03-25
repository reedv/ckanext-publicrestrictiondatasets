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

    def _sysadmins_only(value, context):
        # ensure that only sysadmins are setting a dataset to public
        log = logging.getLogger(__name__)
        
        log.info('\n=====publicrestrictiondatasets:_sysadmins_only(value, context)=====')
        log.info(value)
        log.info(context)
        
        username = context.get('user')
        user = model.User.get(username)
        private = value
        if (not private) and (not user.sysadmin):
            raise toolkit.Invalid('Only sysadmin users may set datasets as public')
        else:
            return value

    def _modify_package_schema(self, schema):
        schema.update({
            'private': [self._sysadmins_only] + schema['private']  #[toolkit.get_validator('ignore_not_sysadmin')]
        })
        return schema

    def create_package_schema(self):
        # let's grab the default schema in our plugin
        schema = super(PublicrestrictiondatasetsPlugin, self).create_package_schema()
        
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(PublicrestrictiondatasetsPlugin, self).update_package_schema()
        
        schema = self._modify_package_schema(schema)
        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []


