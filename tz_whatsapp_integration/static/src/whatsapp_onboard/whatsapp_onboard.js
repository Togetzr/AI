/** @odoo-module **/

import { registry } from '@web/core/registry';
import { useService } from '@web/core/utils/hooks';

const { Component, useState, onWillStart, onMounted } = owl;

export class WAOnboardSettings extends Component {
    async setup() {
        super.setup();
        this.action = useService("action");
        this.orm = useService('orm');

        this.state = useState({
            infos: "",
        });
        var self = this;
        await this._fetchSettingInfos();
        console.log('--this.state',this)
        var infos = this.state.infos
        window.addEventListener('message', (event) => {
            console.log('Data from iframe:', event.data);
            self.orm.call(
                        'res.company', 'set_whatsapp_configurations', [self.props.action.context['active_id'],event.data.phone_number_id,event.data.waba_id],
                        { context: self.context },
                    );
        });
//        window.FB.init({
//                  appId: infos.app_id,
//                  autoLogAppEvents: true,
//                  xfbml: true,
//                  version: infos.api_version
//                });
//        window.fbAsyncInit = function() {
//                window.FB.init({
//                  appId: infos.app_id,
//                  autoLogAppEvents: true,
//                  xfbml: true,
//                  version: infos.api_version
//                });
//              };
//              
//              window.addEventListener('message', (event) => {
//                if (event.origin !== "https://www.facebook.com" && event.origin !== "https://web.facebook.com") return;
//                try {
//                  const data = JSON.parse(event.data);
//                  if (data.type === 'WA_EMBEDDED_SIGNUP' && data.event == 'FINISH') {
//                    console.log('1-->message event: ', data);
//                    self.orm.call(
//                        'res.company', 'set_whatsapp_configurations', [self.props.action.context['active_id'],data.data.phone_number_id,data.data.waba_id],
//                        { context: self.context },
//                    );
//                  }
//                } catch {
//                  console.log('2-->message event: ', event.data);
//                }
//              });
//              
//              this.fbLoginCallback = (response) => {
//                if (response.authResponse) {
//                  const code = response.authResponse.code;
//                  console.log('1-->response: ', code);
//                } else {
//                  console.log('2-->response: ', response);
//                }
//              };
//              
//            this.launchWhatsAppSignup = this.launchWhatsAppSignup.bind(this);
    }
    
//    launchWhatsAppSignup(){
//        var infos = this.state.infos
//        window.FB.login(this.fbLoginCallback, {
//              config_id: infos.FBconfiguration_id,
//              response_type: 'code',
//              override_default_response_type: true,
//              extras: {
//                setup: {},
//                featureType: '',
//                sessionInfoVersion: '3',
//              }
//            });
//    }
    
    async _fetchSettingInfos(parent_id) {
        this.state.infos = await this.orm.call(
            'res.company', 'get_whatsapp_configurations', [this.props.action.context['active_id']],
            { context: this.context },
        )
    }

//    call_action(ev) {
//        const action_id = ev.currentTarget.getAttribute('data-action-id');
//        this.action.doAction(action_id);
//    }

}

WAOnboardSettings.template = 'tz_whatsapp_integration.template_wa_onboard';
registry.category('actions').add('whatsapp_onboard', WAOnboardSettings);
