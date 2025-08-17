/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import FormEditorRegistry from "@website/js/form_editor_registry";

FormEditorRegistry.add('create_reservation', {
    formFields: [{
        type: 'char',
        modelRequired: true,
        name: 'name',
        string: _t('Meeting Title'),
    },
     {
        type: 'datetime',
        modelRequired: true,
        name: 'start',
        string: _t('Start Time'),
    }, {
        type: 'datetime',
        modelRequired: true,
        name: 'stop',
        string: _t('End Time'),
    }, {
        type: 'text',
        name: 'description',
        string: _t('Description'),
    }, {
        type: 'many2many',
        name: 'partner_ids',
        relation: 'res.partner',
        string: _t('Attendees'),
        createAction: 'account.res_partner_action_customer',
    }, {
        type: 'email',
        custom: true,
        required: true,
        fillWith: 'email',
        name: 'email_from',
        string: _t('Your Email'),
    }, {
        type: 'many2one',
        name: 'type_id',
        relation: 'resource.booking.type',
        string: _t('Type'),
        createAction: 'resource_booking.resource_booking_type_action',
    }],
});
