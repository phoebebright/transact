from livesettings import config_register, ConfigurationGroup, PositiveIntegerValue, DecimalValue, StringValue
from django.utils.translation import ugettext_lazy as _


TRANSACT_GROUP = ConfigurationGroup(
    'web',
    _('TransAct web Settings'),
    ordering=1
    )
config_register(DecimalValue(
    TRANSACT_GROUP,
        'PROFIT_MARGIN',
        description = _('Profit margin for whatever'),
        help_text = _("Set your profit margin here."),
        default = '0.10',
))


config_register(StringValue(
        TRANSACT_GROUP,
        'DEFAULT_CURRENCY',
        description=_("Default Currency"),
        help_text=_("Default currency used for creating new users."),
        choices=(('EUR','EUR'), ('GBP','GBP'), ('USD','USD')),
        default="EUR"
    ))


config_register(PositiveIntegerValue(
    TRANSACT_GROUP,
        'EXPIRE_TRANSACTIONS_AFTER_SECONDS',
        description = _('Transaction expiry'),
        help_text = _("by default, transactions will be set to expire after this number of seconds."),
        default = 60 * 5,
))


config_register(DecimalValue(
    TRANSACT_GROUP,
        'DEFAULT_FEE',
        description = _('Default fee'),
        help_text = _("Set percentage charged on each transaction."),
        default = '0.25',
))

config_register(DecimalValue(
    TRANSACT_GROUP,
        'MIN_QUANTITY',
        description = _('Minimum Quantity that can be purchased'),
        help_text = _("Set quantity"),
        default = '0.02',
))

config_register(DecimalValue(
    TRANSACT_GROUP,
        'MAX_QUANTITY',
        description = _('Maximum Quantity that can be purchased'),
        help_text = _("Set quantity"),
        default = '100',
))

config_register(DecimalValue(
    TRANSACT_GROUP,
        'DEFAULT_MIN_POOL_LEVEL',
        description = _('Default recommended level of Quality/Type products in the Pool.'),
        help_text = _("Set default level based on activity"),
        default = '100',
))