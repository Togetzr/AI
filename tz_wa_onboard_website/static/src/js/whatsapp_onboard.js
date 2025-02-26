/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { registry } from '@web/core/registry';
import { Component } from "@odoo/owl";

publicWidget.registry.WebsiteWhatsappOnboarding = publicWidget.Widget.extend({
    
    selector: '.waonboard',
    events: {
        'click .a-submit': 'launchWhatsAppSignup',
    },
    
    init: function () {
        this._super.apply(this, arguments);
        const urlObj = new URL(window.location.href);
        // Get the search parameters
        const params = urlObj.searchParams;

        // Extract parameters into an object
        this.queryParams = {};
        params.forEach((value, key) => {
          this.queryParams[key] = value;
        });

        // Log the parameters
        console.log(this.queryParams);
        console.log("--this",window)
        this.rpc = this.bindService("rpc");
        var self = this;
//        window.parent.postMessage({'action':'success','phone_number_id':'phone_number_id','waba_id':'waba_id'}, '*');
        
        window.FB.init({
                  appId: this.queryParams.app_id,
                  autoLogAppEvents: true,
                  xfbml: true,
                  version: this.queryParams.api_version
                });
        window.fbAsyncInit = function() {
                window.FB.init({
                  appId: this.queryParams.app_id,
                  autoLogAppEvents: true,
                  xfbml: true,
                  version: this.queryParams.api_version
                });
              };
              
              window.addEventListener('message', (event) => {
                if (event.origin !== "https://www.facebook.com" && event.origin !== "https://web.facebook.com") return;
                try {
                  const data = JSON.parse(event.data);
                  if (data.type === 'WA_EMBEDDED_SIGNUP' && data.event == 'FINISH') {
                    console.log('1-->message event: ', data);
                    
                    window.parent.postMessage({'action':'success','phone_number_id':data.data.phone_number_id,'waba_id':data.data.waba_id}, '*');
                  }
                } catch {
                  console.log('2-->message event: ', event.data);
                }
              });
              
              this.fbLoginCallback = (response) => {
                if (response.authResponse) {
                  const code = response.authResponse.code;
                  console.log('1-->response: ', code);
                } else {
                  console.log('2-->response: ', response);
                }
              };
              
            this.launchWhatsAppSignup = this.launchWhatsAppSignup.bind(this);
        
    },
    
    launchWhatsAppSignup(){
        window.FB.login(this.fbLoginCallback, {
              config_id: this.queryParams.FBconfiguration_id,
              response_type: 'code',
              override_default_response_type: true,
              extras: {
                setup: {},
                featureType: '',
                sessionInfoVersion: '3',
              }
            });
    },
    
})

