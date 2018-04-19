from flask_security import current_user
from sqlalchemy import or_, false
from src.utils import ModelResource, operators as ops, AssociationModelResource
from .schemas import User, UserSchema, Role, RoleSchema, UserRole, UserRoleSchema,\
    OrganisationSchema, StoreSchema, UserStoreSchema, CustomerSchema, AddressSchema, CitySchema,\
    LocalitySchema, CustomerAddressSchema, CustomerTransactionSchema, PermissionSchema, UserPermissionSchema,\
    PrinterConfigSchema, RegistrationDetailSchema
from .models import Store, Organisation, UserStore, Customer, Locality, City, Address, CustomerAddress,\
    CustomerTransaction, Permission, UserPermission, PrinterConfig, RegistrationDetail


class UserResource(ModelResource):

    model = User
    schema = UserSchema

    auth_required = True

    roles_accepted = ('admin', 'owner', 'staff')

    optional = ('stores', 'current_login_at', 'current_login_ip', 'created_on',
                'last_login_at', 'last_login_ip', 'login_count', 'confirmed_at', 'permissions')

    filters = {
        'username': [ops.Equal, ops.Contains],
        'name': [ops.Equal, ops.Contains],
        'active': [ops.Boolean],
        'id': [ops.Equal],
        'organisation_id': [ops.Equal, ops.In]
    }

    related_resource = {

    }

    order_by = ['email', 'id', 'name']

    only = ()

    exclude = ()

    def has_read_permission(self, qs):
        if current_user.has_role('admin') or current_user.has_role('owner'):
            return qs.filter(User.organisation_id == current_user.organisation_id)
        else:
            return qs.filter(User.id == current_user.id)

    def has_change_permission(self, obj):
        if current_user.has_role('admin') or current_user.has_role('owner'):
            if current_user.organisation_id == obj.organisation_id:
                return True
        return False

    def has_delete_permission(self, obj):
        if current_user.has_role('admin') or current_user.has_role('owner'):
            if current_user.organisation_id == obj.organisation_id:
                return True
        return False

    def has_add_permission(self, obj):
        if current_user.has_role('admin') or current_user.has_role('owner'):
            if current_user.organisation_id == obj.organisation_id:
                return True
        return False


class StoreResource(ModelResource):
    model = Store
    schema = StoreSchema

    optional = ('localities', 'total_sales', 'retail_brand', 'printer_config', 'registration_details')

    filters = {
        'id': [ops.Equal, ops.In]
    }

    auth_required = True
    roles_accepted = ('admin', 'owner', 'staff')

    def has_read_permission(self, qs):
        return qs.filter(self.model.organisation_id == current_user.organisation_id)

    def has_change_permission(self, obj):
        if obj.organisation_id == current_user.organisation_id and current_user.has_permission('change_store'):

            return True
        return False

    def has_delete_permission(self, obj):
        if obj.organisation_id == current_user.organisation_id and current_user.has_permission('delete_store'):

            return True
        return False

    def has_add_permission(self, obj):
        if obj.organisation_id == current_user.organisation_id and current_user.has_permission('add_store'):

            return True
        return False


class OrganisationResource(ModelResource):
    model = Organisation
    schema = OrganisationSchema

    auth_required = True
    roles_accepted = ('admin', 'owner', 'staff')

    def has_read_permission(self, qs):
        if current_user.has_permission('view_store'):
            return qs.filter(self.model.organisation_id == current_user.organisation_id)

    def has_change_permission(self, obj):
        if obj.organisation_id == current_user.organisation_id and current_user.has_permission('change_store'):
            return True
        return False

    def has_delete_permission(self, obj):
        if obj.organisation_id == current_user.organisation_id and current_user.has_permission('delete_store'):
            return True
        return False

    def has_add_permission(self, obj):
        if obj.organisation_id == current_user.organisation_id and current_user.has_permission('add_store'):
            return True
        return False


class UserStoreResource(AssociationModelResource):

    model = UserStore
    schema = UserStoreSchema

    auth_required = True
    roles_accepted = ('admin', 'owner')

    def has_read_permission(self, qs):
        if current_user.has_permission('view_user_stores'):
            return qs.filter(self.model.store_id.in_(current_user.store_ids)).all()

    def has_change_permission(self, obj, data):
        if current_user.has_permission('change_user_stores') and current_user.has_store_access(obj.store_id):
            return True
        return False

    def has_delete_permission(self, obj, data):
        if current_user.has_permission('delete_user_stores') and current_user.has_store_access(obj.store_id):
            return True
        return False

    def has_add_permission(self, obj, data):
        if current_user.has_permission('add_user_stores'):
            if not current_user.has_store_access(data['store_id']):
                return False
            return True
        return False


class CustomerResource(ModelResource):
    model = Customer
    schema = CustomerSchema

    optional = ('addresses', 'orders', 'retail_brand', 'transactions')

    filters = {
        'name': [ops.Equal, ops.Contains],
        'mobile_number': [ops.Equal, ops.Contains],
        'email': [ops.Equal, ops.Contains],
        'id': [ops.Equal],
        'organisation_id': [ops.Equal],
        'store_id': [ops.Equal, ops.In]
    }

    auth_required = True
    roles_accepted = ('admin', 'owner', 'staff')

    def has_read_permission(self, qs):
        if current_user.has_permission('view_customer'):
            return qs.filter(self.model.organisation_id == current_user.organisation_id)

    def has_change_permission(self, obj):
        if obj.organisation_id == current_user.organisation_id and current_user.has_permission('change_customer'):
            return True
        return False

    def has_delete_permission(self, obj):
        if obj.organisation_id == current_user.organisation_id and current_user.has_permission('delete_customer'):
            return True
        return False

    def has_add_permission(self, objects):
        if not current_user.has_permission('add_customer'):
            return False
        for obj in objects:
            if not str(obj.organisation_id) == current_user.organisation_id:
                return False
        return True


class AddressResource(ModelResource):
    model = Address
    schema = AddressSchema

    auth_required = True
    roles_accepted = ('admin', 'owner', 'staff')

    def has_read_permission(self, qs):
        return qs

    def has_change_permission(self, obj):
        return True

    def has_delete_permission(self, obj):
        return True

    def has_add_permission(self, obj):
        return True


class LocalityResource(ModelResource):
    model = Locality
    schema = LocalitySchema

    auth_required = True
    roles_accepted = ('admin', 'owner', 'staff')

    def has_read_permission(self, qs):
        return qs

    def has_change_permission(self, obj):
        return True

    def has_delete_permission(self, obj):
        return True

    def has_add_permission(self, obj):
        return True


class CityResource(ModelResource):
    model = City
    schema = CitySchema

    auth_required = True
    roles_accepted = ('admin', 'owner', 'staff')

    def has_read_permission(self, qs):
        return qs

    def has_change_permission(self, obj):
        return True

    def has_delete_permission(self, obj):
        return True

    def has_add_permission(self, obj):
        return True


class CustomerAddressResource(AssociationModelResource):

    model = CustomerAddress
    schema = CustomerAddressSchema

    auth_required = True
    roles_accepted = ('admin', 'owner', 'staff')

    def has_read_permission(self, qs):
        return qs

    def has_change_permission(self, obj, data):
        return True

    def has_delete_permission(self, obj, data):
        return True

    def has_add_permission(self, obj, data):
        return True


class CustomerTransactionResource(ModelResource):

    model = CustomerTransaction
    schema = CustomerTransactionSchema

    auth_required = True
    roles_accepted = ('admin', 'owner', 'staff')

    def has_read_permission(self, qs):
        return qs

    def has_change_permission(self, obj):
        return True

    def has_delete_permission(self, obj):
        return True

    def has_add_permission(self, obj):
        return True


class PermissionResource(ModelResource):

    model = Permission
    schema = PermissionSchema

    auth_required = True
    roles_accepted = ('admin', 'owner', 'staff')

    def has_read_permission(self, qs):
        if current_user.has_permission('view_permission'):
            return qs.filter(or_(self.model.is_hidden.is_(False), self.model.is_hidden.is_(None)))
        return False

    def has_change_permission(self, obj):
        if current_user.has_permission('change_user_stores') and current_user.has_store_access(obj.store_id):
            return True
        return False

    def has_delete_permission(self, obj):
        if current_user.has_permission('delete_user_stores') and current_user.has_store_access(obj.store_id):
            return True
        return False

    def has_add_permission(self, objects):
        return False


class UserPermissionResource(AssociationModelResource):

    model = UserPermission
    schema = UserPermissionSchema

    auth_required = True
    roles_accepted = ('admin', 'owner')

    def has_read_permission(self, qs):
        return qs.filter(false())

    def has_change_permission(self, obj, data):
        if current_user.has_permission('change_user_permissions') and \
                        current_user.organisation_id == User.query.with_entities(User.organisation_id)\
                    .filter(User.id == data['user_id']).scalar():
            return True
        return False

    def has_delete_permission(self, obj, data):
        if current_user.has_permission('delete_user_permissions') and \
                        current_user.organisation_id == User.query.with_entities(User.organisation_id)\
                    .filter(User.id == data['user_id']).scalar():
            return True
        return False

    def has_add_permission(self, obj, data):
        if current_user.has_permission('add_user_permission'):
            if current_user.organisation_id == User.query.with_entities(User.organisation_id)\
                    .filter(User.id == data['user_id']).scalar():

                return True
        return False


class RoleResource(ModelResource):
    model = Role
    schema = RoleSchema

    auth_required = True
    roles_accepted = ('admin', 'owner')

    optional = ('permissions',)

    def has_read_permission(self, qs):

        return qs.filter(or_(self.model.is_hidden.is_(False), self.model.is_hidden.is_(None)))

    def has_change_permission(self, obj):
        return False

    def has_delete_permission(self, obj):
        return False

    def has_add_permission(self, obj):
        return False


class UserRoleResource(AssociationModelResource):

    model = UserRole
    schema = UserRoleSchema

    auth_required = True
    roles_accepted = ('admin', 'owner', 'staff')

    def has_read_permission(self, qs):
        return qs.filter(false())

    def has_change_permission(self, obj, data):
        return current_user.organisation_id == User.query.with_entities(User.organisation_id) \
            .filter(User.id == data['user_id']).scalar() and current_user.has_permission('change_user_role')

    def has_delete_permission(self, obj, data):
        return current_user.organisation_id == User.query.with_entities(User.organisation_id) \
            .filter(User.id == data['user_id']).scalar() and current_user.has_permission('delete_user_role')

    def has_add_permission(self, obj, data):
        return current_user.organisation_id == User.query.with_entities(User.organisation_id) \
            .filter(User.id == data['user_id']).scalar() and current_user.has_permission('add_user_role')


class PrinterConfigResource(ModelResource):

    model = PrinterConfig
    schema = PrinterConfigSchema

    auth_required = True
    roles_accepted = ('admin', 'owner', 'staff')

    def has_read_permission(self, qs):
        if current_user.has_permission('view_product_config'):
            return qs.filter(self.model.store_id.in_(current_user.store_ids))
        return qs.filter(false())

    def has_change_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and current_user.has_permission('change_printer_config')

    def has_delete_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and current_user.has_permission('delete_printer_config')

    def has_add_permission(self, objects):
        if not current_user.has_permission('create_product_config'):
            return False
        for obj in objects:
            if not current_user.has_store_access(obj.store_id):
                return False
        return True


class RegistrationDetailResource(ModelResource):

    model = RegistrationDetail
    schema = RegistrationDetailSchema

    auth_required = True
    roles_accepted = ('admin', 'owner', 'staff')

    def has_read_permission(self, qs):
        if current_user.has_permission('view_registration_detail'):
            return qs.filter(self.model.store_id.in_(current_user.store_ids))
        return qs.filter(false())

    def has_change_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and \
               current_user.has_permission('change_registration_detail')

    def has_delete_permission(self, obj):
        return current_user.has_store_access(obj.store_id) and \
               current_user.has_permission('delete_registration_detail')

    def has_add_permission(self, objects):
        if not current_user.has_permission('create_registration_detail'):
            return False
        for obj in objects:
            if not current_user.has_store_access(obj.store_id):
                return False
        return True
