from livesettings import config_register, ConfigurationGroup, PositiveIntegerValue
from django.utils.translation import ugettext_lazy as _

TRANSACT_GROUP = ConfigurationGroup(
    'api',
    _('TransAct api Settings'),
    ordering=2
    )

config_register(PositiveIntegerValue(
    TRANSACT_GROUP,
        'TOKEN_EXPIRY',
        description = _('Expire Token'),
        help_text = _("Set expiry time for token [s]."),
        default = 300,
))
