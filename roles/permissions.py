from flask_principal import Permission, RoleNeed
# list various permission types here

# Create a permission with a single Need, in this case a RoleNeed.
admin_permission = Permission(RoleNeed('Admin'))
sales_permission = Permission(RoleNeed('Sales'))
sales_or_admin_permission = Permission(RoleNeed('Sales'), RoleNeed('Admin'))